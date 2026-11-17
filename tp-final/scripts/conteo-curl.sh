#!/usr/bin/env bash
# Verificación independiente de k6: ¿qué % de requests llega a cada versión?
#
# Uso:  ./scripts/conteo-curl.sh [N]      (N = cantidad de requests, default 100)
#
# Dos fuentes que deberían coincidir:
#  1) Lado cliente: N curls a /version.txt, contados por versión.
#  2) Lado servidor: líneas del log del Ingress controller que fueron al
#     upstream front-canary en el mismo período.
set -euo pipefail

TP_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$TP_DIR"

N="${1:-100}"
URL="${FRONT_URL:-http://terrasense.local}/version.txt"
SALIDA="evidencias/reportes/conteo-$(date +%Y%m%d-%H%M%S).txt"
DESDE="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
PESO="$(kubectl -n terrasense get ingress terrasense-ingress-canary \
  -o jsonpath='{.metadata.annotations.nginx\.ingress\.kubernetes\.io/canary-weight}' 2>/dev/null || echo '?')"

{
  echo "Conteo $(date -Iseconds) | peso configurado: ${PESO}% | ${N} requests"
  echo "--- Lado cliente (curl sin cookies: cada request se sortea de nuevo) ---"
  for _ in $(seq 1 "$N"); do
    curl -s --max-time 5 "$URL" || echo "ERROR"
  done | sort | uniq -c

  # Pausa corta para que el controller termine de escribir los logs.
  sleep 2
  echo "--- Lado servidor (logs del Ingress controller desde ${DESDE}) ---"
  LOGS="$(kubectl -n ingress-nginx logs deploy/ingress-nginx-controller --since-time="$DESDE" 2>/dev/null || true)"
  echo "requests a front-canary: $(grep -c 'front-canary' <<<"$LOGS" || true)"
  echo "requests a front-stable: $(grep -c 'front-stable' <<<"$LOGS" || true)"
} | tee "$SALIDA"

echo "(guardado en $SALIDA)"
