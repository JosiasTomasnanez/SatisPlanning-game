#!/usr/bin/env bash
# Despliega TerraSense completo en un Minikube limpio:
#   cluster → imágenes → base (DB) → back + HPA → front stable + canary → Ingress → /etc/hosts
#
# Uso (desde cualquier carpeta):  ./tp-final/scripts/deploy.sh
# Variables opcionales: MINIKUBE_CPUS (4), MINIKUBE_MEM (6144 MB)
set -euo pipefail

# Trabajamos siempre desde tp-final/ para que las rutas relativas funcionen
# sin importar desde dónde se llame al script.
TP_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$TP_DIR"

NS=terrasense
CPUS="${MINIKUBE_CPUS:-4}"
MEM="${MINIKUBE_MEM:-6144}"

paso() { echo; echo "==> [$(date +%H:%M:%S)] $*"; }

# Fallar temprano con un mensaje claro si falta una herramienta.
for cmd in minikube kubectl docker; do
  command -v "$cmd" >/dev/null || { echo "Falta '$cmd' en el PATH"; exit 1; }
done

# 1) Cluster. Driver docker: Minikube corre como contenedor, no necesita VM.
paso "Iniciando Minikube (driver docker, ${CPUS} CPU, ${MEM} MB)"
if [ "$(minikube status --format '{{.Host}}' 2>/dev/null || true)" = "Running" ]; then
  echo "Minikube ya está corriendo; se reutiliza."
else
  minikube start --driver=docker --cpus="$CPUS" --memory="$MEM"
fi

# ingress: instala ingress-nginx (el que implementa el canary).
# metrics-server: le da al HPA el consumo de CPU de los pods.
paso "Habilitando addons ingress y metrics-server"
minikube addons enable ingress
minikube addons enable metrics-server

# 2) Imágenes. Se construyen DENTRO del Docker de Minikube (docker-env): así
# el cluster las ve sin subirlas a un registry, y por eso los Deployments
# usan imagePullPolicy: IfNotPresent.
paso "Construyendo imágenes dentro de Minikube"
eval "$(minikube docker-env)"
docker build -t terrasense-back:1.0.0 app/back
for v in 1.0.0 1.1.0 1.2.0; do
  docker build --build-arg APP_VERSION="$v" -t "terrasense-front:$v" app/front
done
docker images | grep terrasense

# 3) Esperar al Ingress controller: si aplicamos Ingress antes de que esté
# listo, su webhook de validación rechaza los recursos.
paso "Esperando al Ingress controller"
kubectl -n ingress-nginx wait --for=condition=ready pod \
  -l app.kubernetes.io/component=controller --timeout=300s

# 4) Base: namespace, config/secret y PostgreSQL. La DB primero porque el back
# no pasa la readiness hasta que la DB responde.
paso "Aplicando base (namespace, config, DB)"
kubectl apply -f k8s/base/00-namespace.yaml
kubectl apply -f k8s/base/01-config.yaml
kubectl apply -f k8s/base/02-db.yaml
kubectl -n "$NS" rollout status statefulset/db --timeout=300s

paso "Aplicando back + HPA"
kubectl apply -f k8s/base/03-back.yaml
kubectl apply -f k8s/base/04-hpa.yaml
kubectl -n "$NS" rollout status deployment/back --timeout=300s

paso "Aplicando front stable + canary"
kubectl apply -f k8s/stable/
kubectl apply -f k8s/canary/deployment.yaml -f k8s/canary/service.yaml
kubectl -n "$NS" rollout status deployment/front-stable --timeout=180s
kubectl -n "$NS" rollout status deployment/front-canary --timeout=180s

# 5) Ingress con reintentos: aunque el pod del controller esté "ready", su
# webhook puede tardar unos segundos más en aceptar conexiones.
paso "Aplicando Ingress (API, front y canary)"
for intento in $(seq 1 12); do
  if kubectl apply -f k8s/ingress.yaml -f k8s/canary/ingress-canary.yaml; then
    break
  fi
  if [ "$intento" -eq 12 ]; then echo "No se pudieron aplicar los Ingress"; exit 1; fi
  echo "Webhook del Ingress todavía no disponible; reintento $intento/12 en 5 s..."
  sleep 5
done

# 6) /etc/hosts: los hosts terrasense.local y api.terrasense.local apuntan a
# la IP de Minikube, donde escucha el Ingress controller.
IP="$(minikube ip)"
paso "Actualizando /etc/hosts → ${IP} (pide sudo)"
sudo sed -i '/terrasense\.local/d' /etc/hosts
echo "${IP} terrasense.local api.terrasense.local" | sudo tee -a /etc/hosts >/dev/null
grep terrasense /etc/hosts

paso "Estado final"
kubectl -n "$NS" get pods,svc,ingress,hpa -L track,version
echo
echo "Listo. Probar:  curl -s http://terrasense.local/version.txt"
echo "                curl -s http://api.terrasense.local/api/stats"
