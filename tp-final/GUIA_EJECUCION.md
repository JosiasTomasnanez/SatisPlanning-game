# Guía de ejecución (Ubuntu)

Orden para correr el TP completo y qué capturar en cada paso. Todos los comandos se ejecutan desde
`tp-final/` salvo que se indique otra cosa. Los resultados se cargan después en las tablas
**_completar_** del [`README.md`](README.md).

**Tiempo estimado:** 4 a 5 horas en total, contando la instalación y posibles problemas en la primera corrida.

| Paso | Qué | Tiempo aprox. |
|---|---|---|
| 0 | Preparación de Ubuntu | 30–60 min |
| 1 | Despliegue | 10 min |
| 2 | Línea base TP3 | 45 min |
| 3 | Rollout canary de la v1.1.0 | 25 min |
| 4 | Estrés A/B | 20 min |
| 5 | Demos de rollback con la v1.2.0 | 15 min |
| 6 | Promoción | 5 min |
| 7 | CI y cierre | 30 min + completar README |

## Reglas para la evidencia

- **Hora visible en cada captura y video.** Al abrir cada terminal:
  ```bash
  export PS1='[\D{%H:%M:%S}] \w\$ '     # la hora aparece en cada prompt
  ```
  En los videos, dejar además una terminal chica con `watch -n1 date`.
- **Videos con pantalla partida:** terminal con k6 o el script + terminal con `kubectl ... -w` o el navegador.
- Grabar con **SimpleScreenRecorder** (`sudo apt install simplescreenrecorder`) o con el atajo de GNOME
  `Ctrl+Alt+Shift+R` (graba hasta 30 s por defecto; para videos largos usar SimpleScreenRecorder).
- Guardar con los nombres de la tabla de evidencias del README (sección 5): `evidencias/capturas/...`,
  `evidencias/videos/...`. Los reportes JSON/CSV y los screenshots del navegador los generan los scripts.
- GitHub no acepta archivos de más de 100 MB: si un video es más grande, comprimirlo o subirlo a
  Drive y dejar el link en el README.

---

## 0. Preparación de Ubuntu

```bash
# Docker
sudo apt update && sudo apt install -y docker.io curl python3 git bsdextrautils
sudo usermod -aG docker "$USER" && newgrp docker      # usar docker sin sudo

# Minikube y kubectl
curl -LO https://storage.googleapis.com/minikube/releases/latest/minikube-linux-amd64
sudo install minikube-linux-amd64 /usr/local/bin/minikube && rm minikube-linux-amd64
sudo snap install kubectl --classic

# k6 (repositorio oficial). La versión 1.x incluye el módulo browser.
sudo gpg --no-default-keyring --keyring /usr/share/keyrings/k6-archive-keyring.gpg \
  --keyserver hkp://keyserver.ubuntu.com:80 --recv-keys C5AD17C747E3415A3642D57D77C6C491D6AC1D69
echo "deb [signed-by=/usr/share/keyrings/k6-archive-keyring.gpg] https://dl.k6.io/deb stable main" \
  | sudo tee /etc/apt/sources.list.d/k6.list
sudo apt update && sudo apt install -y k6

# Navegador para k6 browser. Google Chrome (.deb): el chromium de Ubuntu viene por snap
# y suele dar problemas de permisos con k6.
wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
sudo apt install -y ./google-chrome-stable_current_amd64.deb

# Verificar
docker version --format '{{.Server.Version}}'; minikube version; kubectl version --client; k6 version
```

Clonar el repo en la rama del TP:
```bash
git clone https://github.com/LauCallovi/Calidad_software.git
cd Calidad_software && git checkout tp-final && cd tp-final
```

---

## 1. Despliegue

```bash
./scripts/deploy.sh        # pide sudo al final para /etc/hosts
```

Verificar:
```bash
kubectl -n terrasense get pods,svc,ingress,hpa -L track,version
curl -s http://terrasense.local/version.txt                         # → 1.0.0
curl -s -H 'X-Canary: always' http://terrasense.local/version.txt   # → 1.1.0
curl -s http://api.terrasense.local/api/stats
```

📸 **Capturas:**
- `capturas/01-deploy-kubectl.png`: el `kubectl get` de arriba.
- `capturas/01-deploy-navegador.png`: `http://terrasense.local` en el navegador (v1.0.0).

> Si `kubectl get hpa` muestra `<unknown>` en CPU, esperar 1–2 minutos: metrics-server tarda en juntar datos.

---

## 2. Línea base (TP3)

Antes de tocar el front se mide el back, para tener contra qué comparar.

### 2.1 Smoke y load
```bash
k6 run k6/smoke.js 2>&1 | tee evidencias/reportes/tp3-smoke.txt
k6 run k6/load.js  2>&1 | tee evidencias/reportes/tp3-load.txt     # 5 min a 67 req/s
```
📸 `capturas/02-smoke.png`, `capturas/02-load.png`: el resumen final de k6, con los thresholds en verde.

### 2.2 Stress + HPA
Terminal 2:
```bash
watch -n2 'date; kubectl -n terrasense get hpa; kubectl -n terrasense get pods -l app=back'
```
Terminal 1:
```bash
k6 run k6/stress.js 2>&1 | tee evidencias/reportes/tp3-stress.txt    # ~10 min, puede abortar al encontrar el quiebre
```
🎥 `videos/02-stress-hpa.mp4`: k6 y el HPA escalando (réplicas 2 → N).
Anotar: req/s y p95 en cada escalón, réplicas máximas, si abortó y en qué escalón.

### 2.3 E1: eliminar un pod con carga estable
Esperar a que el HPA vuelva a 2 réplicas (`kubectl -n terrasense get hpa`, unos minutos).

Terminal 1 (carga, 90 s):
```bash
k6 run k6/e1-carga-estable.js 2>&1 | tee evidencias/reportes/tp3-e1.txt
```
Terminal 2 (navegador, al mismo tiempo):
```bash
k6 run -e DURATION_S=60 k6/browser-ux.js
```
Terminal 3, unos **20 s después** de arrancar la carga:
```bash
date; kubectl -n terrasense delete pod "$(kubectl -n terrasense get pods -l app=back -o name | head -1)"
kubectl -n terrasense get pods -l app=back -w
```
🎥 `videos/03-e1-pod-eliminado.mp4`. Los screenshots `capturas/e1-ux-NN.png` se generan solos.
Anotar: cantidad de errores (`errores_e1`), hora del primero y del último (líneas `ERR` del log) → ventana de errores.

### 2.4 E2: spike de CPU y OOM
```bash
k6 run -e MODE=cpu k6/spike.js 2>&1 | tee evidencias/reportes/tp3-spike-cpu.txt
```
Esperar a que se estabilice y después:
```bash
k6 run -e MODE=oom k6/spike.js 2>&1 | tee evidencias/reportes/tp3-spike-oom.txt
```
En otra terminal, durante el OOM:
```bash
kubectl -n terrasense get pods -l app=back -w
# después: confirmar el motivo del reinicio
kubectl -n terrasense describe pods -l app=back | grep -A3 "Last State"     # → Reason: OOMKilled
```
🎥 `videos/04-e2-oom.mp4`: pods pasando a `OOMKilled` y reiniciándose (RESTARTS sube).
📸 `capturas/04-oomkilled.png`: el `describe` con `OOMKilled`.

> 1500 req/s puede ser demasiado para una notebook. Si la PC se cuelga, bajar el `target` del pico
> en `k6/spike.js` (por ejemplo a 600) y anotarlo en el informe.

Antes de seguir, verificar que el back quedó sano:
`kubectl -n terrasense get pods -l app=back` (todos `Running` y `READY 1/1`).

---

## 3. Rollout canary de la v1.1.0

### 3.1 Etapa 0 a mano (para la captura)
1. Abrir `http://terrasense.local` en una ventana normal → v1.0.0.
2. En otra ventana (o en modo incógnito), F12 → Consola:
   ```js
   document.cookie = "canary=always; path=/"; location.reload();
   ```
   → aparece la v1.1.0 (verde, banner "ESTÁS VIENDO LA VERSIÓN CANARY 1.1.0").

📸 `capturas/03-etapa0-cookie.png`: las dos ventanas lado a lado, con peso 0.

### 3.2 Rollout automático
Terminal 1:
```bash
./scripts/rollout.sh          # etapa 0 → 10 → 25 → 50 → 100, ~25 min
# ensayo corto si hace falta:  DURATION=1m ./scripts/rollout.sh
```
Terminal 2, **durante cada etapa** (cuando el script muestra "ETAPA peso-N"):
```bash
./scripts/conteo-curl.sh 100
```
🎥 `videos/05-rollout-1.1.0.mp4`: el script avanzando de etapa (se puede grabar solo el principio y el final de cada etapa).
📸 `capturas/05-conteo-peso-NN.png` en cada peso; `capturas/05-bitacora.png` con:
```bash
column -s, -t < evidencias/reportes/bitacora.csv
```
**No promover todavía:** el estrés A/B necesita la stable en 1.0.0.

---

## 4. Estrés A/B (hipótesis)

Condiciones comparables: canary con 2 réplicas (igual que la stable) y peso 0.
```bash
kubectl -n terrasense scale deployment front-canary --replicas=2
kubectl -n terrasense rollout status deployment/front-canary
./scripts/peso.sh 0
```
Cerrar otros programas pesados. Después, una corrida tras otra (~9 min cada una):
```bash
TARGET=stable k6 run k6/front-stress.js 2>&1 | tee evidencias/reportes/estres-front-stable.txt
TARGET=canary k6 run k6/front-stress.js 2>&1 | tee evidencias/reportes/estres-front-canary.txt
```
📸 `capturas/04-estres-stable.png`, `capturas/04-estres-canary.png`: la tabla por escalón que muestra k6 al final.

Volver a 1 réplica:
```bash
kubectl -n terrasense scale deployment front-canary --replicas=1
```
Cargar los datos en la sección 3.4 del README desde `estres-front-*.json`.

---

## 5. Demos de rollback con la v1.2.0 (pantalla en blanco)

### 5.1 Demo A: la etapa 0 la frena (ningún usuario expuesto)
```bash
VERSION_CANARY=1.2.0 ./scripts/rollout.sh
```
Resultado esperado: `ETAPA 0 FALLA: 3 de 3 visitas con pantalla en blanco`, y la fila ROLLBACK en la bitácora.
Los screenshots `capturas/etapa-0-visita-0N-v1.2.0-BLANCA.png` se generan solos.

Mientras el canary tiene la 1.2.0 (peso 0), abrir el navegador con la cookie `canary=always`
(como en 3.1) y F12 → Consola:
📸 `capturas/06-consola-typeerror.png`: pantalla en blanco + `TypeError: Cannot read properties of undefined (reading 'api')`.
📸 `capturas/06-network-200.png`: pestaña Red (Network) con el HTML y el JS en **200**. Demuestra por qué un chequeo HTTP no la detecta.

### 5.2 Demo B: llega a usuarios reales y se revierte
```bash
VERSION_CANARY=1.2.0 SALTEAR_ETAPA0=1 PESOS="25" DURATION=2m ./scripts/rollout.sh
```
Resultado esperado: el split da los thresholds **OK** (todo responde 200), pero el navegador encuentra
pantallas en blanco → `ROLLBACK completo: tráfico 100% en stable en X s`.
🎥 `videos/06-rollback-1.2.0.mp4` (**el video más importante del TP**): el script, el navegador en blanco y el rollback.
Anotar el **tiempo de rollback** (también queda en la bitácora).

---

## 6. Promoción de la v1.1.0

```bash
SOLO_PROMOVER=1 VERSION_CANARY=1.1.0 ./scripts/rollout.sh
kubectl -n terrasense get pods -L track,version
curl -s http://terrasense.local/version.txt        # → 1.1.0 (ahora desde la stable)
```
📸 `capturas/07-promocion.png`: pods stable en 1.1.0, canary con 0 réplicas.

> Después de promover, la stable es la 1.1.0: para cualquier corrida posterior usar `VERSION_STABLE=1.1.0`.
> `k8s/stable/deployment.yaml` quedó modificado por la promoción: commitearlo junto con las evidencias.

---

## 7. CI y cierre

1. GitHub → Actions:
   - 📸 `capturas/07-ci-rojo.png`: run **#43995990963** (horusec en rojo, build skipped).
   - 📸 `capturas/07-ci-verde.png`: run **#44008882096** (los tres jobs en verde).
2. Completar las tablas **_completar_** del `README.md` (bitácora, conteos, estrés, veredicto,
   aprendizaje) con los datos de `evidencias/reportes/`. Para ver un JSON:
   `python3 -m json.tool evidencias/reportes/peso-25-split.json`.
3. Commitear las evidencias y los YAML modificados (peso y promoción):
   ```bash
   git add evidencias k8s README.md && git commit -m "docs(tp-final): evidencias de ejecucion"
   git push
   ```

Para volver a empezar desde cero: `minikube delete` y otra vez `./scripts/deploy.sh`.

---

## Problemas frecuentes

| Síntoma | Causa probable | Solución |
|---|---|---|
| `ErrImageNeverPull` / `ImagePullBackOff` | Las imágenes se construyeron fuera del Docker de Minikube | `eval $(minikube docker-env)` y repetir el build, o volver a correr `deploy.sh` |
| `failed calling webhook "validate.nginx.ingress..."` | El Ingress controller todavía no está listo | Esperar y reintentar (`deploy.sh` ya reintenta 12 veces) |
| `curl: Could not resolve host terrasense.local` | Falta la entrada en `/etc/hosts` | `grep terrasense /etc/hosts`; debe tener la IP de `minikube ip` |
| Front en `CrashLoopBackOff` | Permisos de nginx con el UID no root | `kubectl -n terrasense logs deploy/front-stable`; verificar los `emptyDir` en `/var/cache/nginx` y `/tmp` |
| Back no pasa a `Ready` | La DB no está lista o falta el Secret | `kubectl -n terrasense get secret db-secret`; `kubectl -n terrasense logs deploy/back` |
| k6 browser: `could not find browser` | No encuentra Chrome | `export K6_BROWSER_EXECUTABLE_PATH=/usr/bin/google-chrome` |
| HPA en `<unknown>` | metrics-server sin datos todavía | Esperar 1–2 min; `minikube addons list | grep metrics` |
| `rollout.sh`: "sin reporte del split" | k6 se cortó | Leer `evidencias/reportes/peso-N-split.log` |
| La PC se cuelga en stress/spike | El generador de carga y el cluster comparten la máquina | Bajar los `target` de los escalones y anotarlo; revisar las iteraciones descartadas |
