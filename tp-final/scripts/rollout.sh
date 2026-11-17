#!/usr/bin/env bash
# Ejecuta el PLAN DE ROLLOUT del canary de forma automática y reproducible.
#
#   Etapa 0: peso 0 + navegador forzado al canary (cookie) → ¿la versión nueva
#            se ve bien, sin exponer a ningún usuario real?
#   Etapas 10 → 25 → 50 → 100: en cada peso corren en paralelo el split (k6
#            HTTP) y el navegador (k6 browser). Se AVANZA solo si:
#              - los thresholds del split dan OK,
#              - hay 0 pantallas en blanco,
#              - p95 de página canary ≤ p95 stable + 10%  (o la diferencia < 5 ms).
#            Si algo falla → ROLLBACK (peso 0), se mide cuánto tardó y se corta.
#   PROMOVER=1: al terminar bien, la stable pasa a la versión nueva y el canary se apaga.
#
# Cada etapa queda registrada en evidencias/reportes/bitacora.csv.
#
# Uso (desde tp-final/ o desde cualquier lado):
#   ./scripts/rollout.sh                                   # plan completo con la 1.1.0
#   DURATION=1m ./scripts/rollout.sh                        # versión corta para ensayar
#   PROMOVER=1 ./scripts/rollout.sh                         # plan + promoción
#   SOLO_PROMOVER=1 ./scripts/rollout.sh                    # solo promoción (ya validado)
#   VERSION_CANARY=1.2.0 ./scripts/rollout.sh               # demo: la etapa 0 frena la rota
#   VERSION_CANARY=1.2.0 SALTEAR_ETAPA0=1 PESOS="25" ./scripts/rollout.sh
#                                                           # demo: rollback con tráfico real
#
# Sin "set -e" a propósito: k6 devuelve código 99 cuando fallan los thresholds
# y ese caso lo manejamos nosotros (rollback), no debe cortar el script.
set -uo pipefail

TP_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$TP_DIR"

NS=terrasense
FRONT="${FRONT_URL:-http://terrasense.local}"
PESOS="${PESOS:-10 25 50 100}"
VERSION_STABLE="${VERSION_STABLE:-1.0.0}"
VERSION_CANARY="${VERSION_CANARY:-1.1.0}"
RATE="${RATE:-20}"
DURATION="${DURATION:-5m}"
N_BROWSER="${N_BROWSER:-20}"
PROMOVER="${PROMOVER:-0}"
SOLO_PROMOVER="${SOLO_PROMOVER:-0}"
SALTEAR_ETAPA0="${SALTEAR_ETAPA0:-0}"
# Criterio de latencia, fijado ANTES de ejecutar (ver README, plan de rollout).
TOLERANCIA_PCT=10
TOLERANCIA_MS=5

REP=evidencias/reportes
BITACORA="$REP/bitacora.csv"
mkdir -p "$REP" evidencias/capturas

for cmd in kubectl k6 python3 curl; do
  command -v "$cmd" >/dev/null || { echo "Falta '$cmd' en el PATH"; exit 1; }
done

# ---------- utilidades ----------

titulo() { echo; echo "================ [$(date '+%Y-%m-%d %H:%M:%S')] $* ================"; }

# Lee un campo de un JSON de evidencia (ej. jget archivo.json p95_ms.pagina_canary).
# Si el archivo no existe (k6 se cortó), devuelve vacío.
jget() {
  python3 - "$1" "$2" <<'PY' 2>/dev/null || echo ""
import json, sys
d = json.load(open(sys.argv[1]))
for k in sys.argv[2].split("."):
    d = d[k]
print(d)
PY
}

# Comparación de decimales (bash solo compara enteros).
mayor_que() { awk -v a="$1" -v b="$2" 'BEGIN { exit !(a + 0 > b + 0) }'; }

registrar() {
  # Columnas: inicio,fin,etapa,version,peso,pct_observado,visitas,p95_canary_ms,
  #           p95_stable_ms,err_canary,assets_rotos,pantallas_blancas,decision,motivo
  if [ ! -f "$BITACORA" ]; then
    echo "inicio,fin,etapa,version,peso,pct_observado,visitas,p95_canary_ms,p95_stable_ms,err_canary,assets_rotos,pantallas_blancas,decision,motivo" > "$BITACORA"
  fi
  local motivo="${14//,/;}"   # sin comas, para no romper el CSV
  echo "$1,$2,$3,$4,$5,$6,$7,$8,$9,${10},${11},${12},${13},${motivo}" >> "$BITACORA"
}

# Rollback = peso 0. Medimos el tiempo hasta que 20 requests seguidos ya no
# reciben la versión canary: ese es el tiempo real de "cortar la exposición".
rollback() {
  local t0 t1 i en_canary
  t0=$(date +%s.%N)
  ./scripts/peso.sh 0
  for i in $(seq 1 60); do
    en_canary=$(for _ in $(seq 1 20); do curl -s --max-time 2 "$FRONT/version.txt"; echo; done | grep -c "^${VERSION_CANARY}$" || true)
    [ "$en_canary" -eq 0 ] && break
    sleep 1
  done
  t1=$(date +%s.%N)
  DURACION_ROLLBACK=$(awk -v a="$t0" -v b="$t1" 'BEGIN { printf "%.1f", b - a }')
  echo ">>> ROLLBACK completo: tráfico 100% en stable en ${DURACION_ROLLBACK} s"
}

# Deja el Deployment canary con la imagen VERSION_CANARY y al menos 1 réplica.
# Siempre con peso 0 primero: nunca cambiamos la imagen con usuarios adentro.
preparar_canary() {
  local imagen replicas
  imagen=$(kubectl -n "$NS" get deploy front-canary -o jsonpath='{.spec.template.spec.containers[0].image}')
  replicas=$(kubectl -n "$NS" get deploy front-canary -o jsonpath='{.spec.replicas}')
  if [ "$imagen" != "terrasense-front:${VERSION_CANARY}" ] || [ "${replicas:-0}" -eq 0 ]; then
    titulo "Preparando canary con terrasense-front:${VERSION_CANARY} (peso 0)"
    ./scripts/peso.sh 0
    kubectl -n "$NS" patch deployment front-canary -p "{\"metadata\":{\"labels\":{\"version\":\"${VERSION_CANARY}\"}},\"spec\":{\"template\":{\"metadata\":{\"labels\":{\"version\":\"${VERSION_CANARY}\"}},\"spec\":{\"containers\":[{\"name\":\"front\",\"image\":\"terrasense-front:${VERSION_CANARY}\"}]}}}}"
    [ "${replicas:-0}" -eq 0 ] && kubectl -n "$NS" scale deployment front-canary --replicas=1
    kubectl -n "$NS" rollout status deployment/front-canary --timeout=180s || exit 1
  fi
}

# Promoción en ESTE orden (si se invierte, hay una ventana en la que el
# tráfico vuelve a la versión vieja):
#   1) la stable pasa a la imagen nueva (el canary, con peso 100, sigue
#      atendiendo mientras tanto)
#   2) peso 0 → todo el tráfico a la stable, que ya es la versión nueva
#   3) recién ahí el canary baja a 0 réplicas
promover() {
  local inicio fin v
  inicio=$(date -Iseconds)
  titulo "PROMOCIÓN: front-stable → ${VERSION_CANARY}"
  sed -i -E "s#image: terrasense-front:[0-9.]+#image: terrasense-front:${VERSION_CANARY}#; s#(version: )\"[0-9.]+\"#\1\"${VERSION_CANARY}\"#" k8s/stable/deployment.yaml
  kubectl apply -f k8s/stable/deployment.yaml
  kubectl -n "$NS" rollout status deployment/front-stable --timeout=300s || { echo "La stable no terminó de actualizarse; NO se toca el peso"; exit 1; }
  # Verificación: forzando la stable con el header, ¿responde la versión nueva?
  v=$(curl -s -H 'X-Canary: never' "$FRONT/version.txt")
  echo "stable responde: ${v}"
  ./scripts/peso.sh 0
  kubectl -n "$NS" scale deployment front-canary --replicas=0
  fin=$(date -Iseconds)
  registrar "$inicio" "$fin" "promocion" "$VERSION_CANARY" 0 "" "" "" "" "" "" "" "PROMOCION" "stable ahora sirve ${v}; canary a 0 replicas"
  kubectl -n "$NS" get pods -L track,version
}

# ---------- solo promoción ----------
if [ "$SOLO_PROMOVER" = "1" ]; then
  promover
  exit 0
fi

titulo "ROLLOUT canary ${VERSION_CANARY} (stable ${VERSION_STABLE}) | pesos: ${PESOS} | split ${RATE}/s x ${DURATION}"
preparar_canary

# ---------- Etapa 0: peso 0 + cookie canary=always ----------
if [ "$SALTEAR_ETAPA0" != "1" ]; then
  titulo "ETAPA 0: peso 0, navegador forzado al canary (3 visitas)"
  inicio=$(date -Iseconds)
  ./scripts/peso.sh 0
  sleep 5   # dar tiempo a que el Ingress controller recargue la configuración
  k6 run -e ETAPA=etapa-0 -e FORZAR_CANARY=1 -e N=3 -e FRONT_URL="$FRONT" \
    -e VERSION_STABLE="$VERSION_STABLE" -e VERSION_CANARY="$VERSION_CANARY" \
    k6/browser-canary.js 2>&1 | tee "$REP/etapa-0-browser.log"
  rc=${PIPESTATUS[0]}
  fin=$(date -Iseconds)
  blancas=$(jget "$REP/etapa-0-browser.json" pantallas_blancas)
  vistas_c=$(jget "$REP/etapa-0-browser.json" vistas_canary)

  motivo=""
  if [ -z "$blancas" ]; then motivo="sin reporte del navegador (rc=${rc})"
  elif [ "$blancas" -gt 0 ]; then motivo="${blancas} de 3 visitas con pantalla en blanco"
  elif [ "$rc" -ne 0 ]; then motivo="k6 browser terminó con error (rc=${rc})"
  elif [ "${vistas_c:-0}" -ne 3 ]; then motivo="la cookie no enrutó al canary (${vistas_c}/3 visitas en ${VERSION_CANARY})"
  fi

  if [ -n "$motivo" ]; then
    echo ">>> ETAPA 0 FALLA: ${motivo}. Ningún usuario real fue expuesto (peso 0)."
    registrar "$inicio" "$fin" "etapa-0" "$VERSION_CANARY" 0 "" 3 "" "" "" "" "${blancas:-}" "ROLLBACK" "$motivo"
    exit 1
  fi
  echo ">>> ETAPA 0 OK: el canary se ve bien con peso 0."
  registrar "$inicio" "$fin" "etapa-0" "$VERSION_CANARY" 0 "" 3 "" "" "" "" 0 "AVANZA" "3/3 visitas forzadas OK"
fi

# ---------- Etapas por peso ----------
P95_STABLE_REF=""
for P in $PESOS; do
  ETAPA="peso-${P}"
  titulo "ETAPA ${ETAPA}: ${P}% del tráfico al canary"
  inicio=$(date -Iseconds)
  ./scripts/peso.sh "$P"
  sleep 5

  # Split en segundo plano (dura DURATION) y navegador en primer plano: el
  # navegador ve la UI mientras el split genera tráfico con el mismo peso.
  k6 run --quiet -e ETAPA="$ETAPA" -e PESO="$P" -e RATE="$RATE" -e DURATION="$DURATION" \
    -e FRONT_URL="$FRONT" -e VERSION_STABLE="$VERSION_STABLE" -e VERSION_CANARY="$VERSION_CANARY" \
    k6/front-canary-split.js > "$REP/${ETAPA}-split.log" 2>&1 &
  PID_SPLIT=$!

  k6 run -e ETAPA="$ETAPA" -e N="$N_BROWSER" -e FRONT_URL="$FRONT" \
    -e VERSION_STABLE="$VERSION_STABLE" -e VERSION_CANARY="$VERSION_CANARY" \
    k6/browser-canary.js 2>&1 | tee "$REP/${ETAPA}-browser.log"
  RC_B=${PIPESTATUS[0]}

  echo "... navegador terminado; esperando que termine el split (${DURATION})"
  wait "$PID_SPLIT"
  RC_S=$?
  tail -n 10 "$REP/${ETAPA}-split.log"
  fin=$(date -Iseconds)

  S="$REP/${ETAPA}-split.json"
  B="$REP/${ETAPA}-browser.json"
  pct=$(jget "$S" porcentaje_canary_observado)
  visitas=$(jget "$S" visitas.total)
  vc=$(jget "$S" visitas.canary)
  vs=$(jget "$S" visitas.stable)
  p95c=$(jget "$S" p95_ms.pagina_canary)
  p95s=$(jget "$S" p95_ms.pagina_stable)
  errc=$(jget "$S" tasa_error.canary)
  assets=$(jget "$S" assets_rotos.cantidad)
  blancas=$(jget "$B" pantallas_blancas)

  # Con peso 100 no hay visitas a la stable: se compara contra el último p95
  # stable medido (el de la etapa anterior).
  if [ -n "$vs" ] && [ "$vs" -gt 0 ]; then P95_STABLE_REF="$p95s"; fi

  motivos=()
  [ -z "$pct" ] && motivos+=("sin reporte del split")
  [ "$RC_S" -ne 0 ] && motivos+=("thresholds del split fallaron (rc=${RC_S})")
  [ -z "$blancas" ] && motivos+=("sin reporte del navegador")
  [ -n "$blancas" ] && [ "$blancas" -gt 0 ] && motivos+=("${blancas} pantallas en blanco")
  [ -n "$blancas" ] && [ "$blancas" -eq 0 ] && [ "$RC_B" -ne 0 ] && motivos+=("k6 browser terminó con error (rc=${RC_B})")
  [ -n "$vc" ] && [ "$vc" -eq 0 ] && motivos+=("el canary no recibió visitas")
  if [ -n "$p95c" ] && [ -n "$P95_STABLE_REF" ]; then
    limite=$(awk -v s="$P95_STABLE_REF" -v p="$TOLERANCIA_PCT" 'BEGIN { printf "%.2f", s * (1 + p / 100) }')
    diferencia=$(awk -v c="$p95c" -v s="$P95_STABLE_REF" 'BEGIN { printf "%.2f", c - s }')
    if mayor_que "$p95c" "$limite" && ! mayor_que "$TOLERANCIA_MS" "$diferencia"; then
      motivos+=("p95 canary ${p95c} ms > stable ${P95_STABLE_REF} ms +${TOLERANCIA_PCT}% (dif ${diferencia} ms)")
    fi
  fi

  if [ "${#motivos[@]}" -gt 0 ]; then
    motivo=$(IFS='; '; echo "${motivos[*]}")
    echo ">>> ETAPA ${ETAPA} FALLA: ${motivo}"
    rollback
    registrar "$inicio" "$(date -Iseconds)" "$ETAPA" "$VERSION_CANARY" "$P" "$pct" "$visitas" "$p95c" "$P95_STABLE_REF" "$errc" "$assets" "$blancas" \
      "ROLLBACK" "${motivo}; rollback en ${DURACION_ROLLBACK} s"
    exit 1
  fi

  echo ">>> ETAPA ${ETAPA} OK: observado ${pct}% | p95 canary ${p95c} ms vs stable ${P95_STABLE_REF} ms | avanza"
  registrar "$inicio" "$fin" "$ETAPA" "$VERSION_CANARY" "$P" "$pct" "$visitas" "$p95c" "$P95_STABLE_REF" "$errc" "$assets" "$blancas" \
    "AVANZA" "criterios cumplidos"
done

titulo "Plan completo: todas las etapas cumplieron los criterios"
if [ "$PROMOVER" = "1" ]; then
  promover
else
  echo "El canary quedó con el último peso del plan. Peso 100 NO es promoción:"
  echo "la stable sigue declarada en ${VERSION_STABLE}. Para promover:"
  echo "  SOLO_PROMOVER=1 VERSION_CANARY=${VERSION_CANARY} ./scripts/rollout.sh"
fi
echo
column -s, -t < "$BITACORA" 2>/dev/null || cat "$BITACORA"
