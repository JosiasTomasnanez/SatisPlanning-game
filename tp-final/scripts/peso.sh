#!/usr/bin/env bash
# Cambia el % de tráfico que va al canary.
#
# Uso:  ./scripts/peso.sh 25
#
# Hace tres cosas:
#  1) annotate en el cluster → el Ingress controller recarga en segundos,
#     sin reiniciar pods.
#  2) actualiza el YAML → el repo refleja lo que hay en el cluster (si alguien
#     vuelve a aplicar el YAML, no pisa el peso con un valor viejo).
#  3) registra la hora del cambio → evidencia para cruzar con métricas y videos.
set -euo pipefail

TP_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$TP_DIR"

NS=terrasense
INGRESS=terrasense-ingress-canary
YAML=k8s/canary/ingress-canary.yaml
LOG=evidencias/reportes/cambios-de-peso.log

PESO="${1:-}"
if ! [[ "$PESO" =~ ^[0-9]+$ ]] || [ "$PESO" -gt 100 ]; then
  echo "Uso: $0 <peso 0-100>"
  exit 1
fi

# Peso actual, para dejar en el log "de cuánto a cuánto" cambió.
ANTERIOR="$(kubectl -n "$NS" get ingress "$INGRESS" \
  -o jsonpath='{.metadata.annotations.nginx\.ingress\.kubernetes\.io/canary-weight}' 2>/dev/null || echo '?')"

kubectl -n "$NS" annotate ingress "$INGRESS" \
  nginx.ingress.kubernetes.io/canary-weight="$PESO" --overwrite >/dev/null

sed -i -E "s/(nginx\.ingress\.kubernetes\.io\/canary-weight: )\"[0-9]+\"/\1\"${PESO}\"/" "$YAML"

mkdir -p "$(dirname "$LOG")"
LINEA="$(date -Iseconds) peso ${ANTERIOR:-?} -> ${PESO}"
echo "$LINEA" >> "$LOG"
echo "$LINEA"
