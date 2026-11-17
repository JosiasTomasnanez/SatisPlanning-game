import exec from 'k6/execution';
import { Counter, Trend, Rate } from 'k6/metrics';
import { cargarPagina, VERSION_STABLE, VERSION_CANARY } from './front-common.js';

// ESTRÉS A/B del front (Actividad 2). Misma carga creciente contra cada
// versión por separado, para contrastar la hipótesis:
//   "la v1.1.0 no empeora el p95 de carga de página más de 10% vs la v1.0.0,
//    y ambas sostienen 200 cargas/s con < 1% de errores".
//
//   TARGET=stable k6 run k6/front-stress.js
//   TARGET=canary k6 run k6/front-stress.js
//
// Condiciones comparables (ver README): canary escalado a 2 réplicas (igual
// que la stable) y peso 0. El header X-Canary FUERZA la versión, así cada
// corrida mide UNA sola versión aunque las dos estén desplegadas.

const TARGET = (__ENV.TARGET || 'stable').toLowerCase();
if (TARGET !== 'stable' && TARGET !== 'canary') {
  throw new Error('TARGET debe ser "stable" o "canary"');
}
const HEADERS = { 'X-Canary': TARGET === 'canary' ? 'always' : 'never' };
const VERSION_ESPERADA = __ENV.VERSION_ESPERADA
  || (TARGET === 'canary' ? VERSION_CANARY : VERSION_STABLE);

// Mesetas de carga (cargas de página por segundo) y cuánto dura cada una.
// Antes de cada meseta hay 10 s de subida para no meter un salto brusco.
const SUBIDA_S = 10;
const MESETAS = [
  { carga: 50, seg: 60 },
  { carga: 100, seg: 60 },
  { carga: 200, seg: 120 }, // ← el escalón de la hipótesis
  { carga: 400, seg: 120 },
  { carga: 800, seg: 120 },
];

// Tabla de tiempos para saber en qué escalón estamos (tag "escalon").
// Durante las subidas el tag es "subida": no mezclamos esos datos con los de
// la meseta, porque ahí la carga todavía no es la del escalón.
const TRAMOS = [];
const STAGES = [];
let t = 0;
for (const m of MESETAS) {
  TRAMOS.push({ desde: t, hasta: t + SUBIDA_S, escalon: 'subida' });
  t += SUBIDA_S;
  TRAMOS.push({ desde: t, hasta: t + m.seg, escalon: String(m.carga) });
  t += m.seg;
  STAGES.push({ target: m.carga, duration: `${SUBIDA_S}s` });
  STAGES.push({ target: m.carga, duration: `${m.seg}s` });
}
STAGES.push({ target: 0, duration: '10s' });

function escalonActual() {
  const seg = (Date.now() - exec.scenario.startTime) / 1000;
  const tramo = TRAMOS.find((x) => seg >= x.desde && seg < x.hasta);
  return tramo ? tramo.escalon : 'bajada';
}

const cargaPagina = new Trend('carga_pagina', true);
const errCarga = new Rate('err_carga');
const bytesPagina = new Trend('bytes_pagina');
// Si aparece otra versión, el header no funcionó y la medición no sirve.
const versionInesperada = new Counter('version_inesperada');

// Los thresholds "triviales" (>=0) de los otros escalones no evalúan nada:
// son el truco de k6 para que el resumen incluya el p95 de cada escalón.
const thresholds = {
  'err_carga{escalon:200}': ['rate<0.01'],
  'carga_pagina{escalon:200}': ['p(95)<300'],
  version_inesperada: ['count==0'],
};
for (const m of MESETAS) {
  if (m.carga !== 200) {
    thresholds[`carga_pagina{escalon:${m.carga}}`] = ['p(95)>=0'];
    thresholds[`err_carga{escalon:${m.carga}}`] = ['rate>=0'];
  }
}

export const options = {
  scenarios: {
    rampa: {
      executor: 'ramping-arrival-rate',
      startRate: 0,
      timeUnit: '1s',
      stages: STAGES,
      preAllocatedVUs: 100,
      maxVUs: 1500,
    },
  },
  thresholds,
};

export default function () {
  const escalon = escalonActual();
  const tags = { escalon };
  const p = cargarPagina(HEADERS, tags);

  // Error de carga = HTML no 200 o algún asset roto: para el usuario es lo mismo.
  const fallo = !p.ok || p.assetsRotos > 0;
  errCarga.add(fallo, tags);
  if (p.ok) {
    cargaPagina.add(p.duracionPagina, tags);
    bytesPagina.add(p.bytes);
  }
  if (p.version !== null && p.version !== VERSION_ESPERADA) versionInesperada.add(1);
}

export function handleSummary(data) {
  const v = (nombre, campo) => {
    const m = data.metrics[nombre];
    return m && m.values[campo] !== undefined ? m.values[campo] : null;
  };
  const escalones = {};
  for (const m of MESETAS) {
    const passes = v(`err_carga{escalon:${m.carga}}`, 'passes') || 0;
    const fails = v(`err_carga{escalon:${m.carga}}`, 'fails') || 0;
    escalones[m.carga] = {
      cargas: passes + fails,
      p95_ms: v(`carga_pagina{escalon:${m.carga}}`, 'p(95)'),
      tasa_error: v(`err_carga{escalon:${m.carga}}`, 'rate'),
    };
  }
  const ok = Object.values(data.metrics).every((m) =>
    !m.thresholds || Object.values(m.thresholds).every((x) => x.ok));

  const reporte = {
    target: TARGET,
    version_esperada: VERSION_ESPERADA,
    escalones,
    bytes_por_pagina_promedio: v('bytes_pagina', 'avg'),
    version_inesperada: v('version_inesperada', 'count') || 0,
    // Iteraciones que k6 NO pudo lanzar por falta de VUs: si es alto, el
    // límite lo puso la máquina que genera la carga, no el sistema medido.
    iteraciones_descartadas: v('dropped_iterations', 'count') || 0,
    thresholds_ok: ok,
    generado: new Date().toISOString(),
  };

  const filas = MESETAS.map((m) => {
    const e = escalones[m.carga];
    const p95 = e.p95_ms === null ? '-' : `${e.p95_ms.toFixed(1)} ms`;
    const err = e.tasa_error === null ? '-' : `${(100 * e.tasa_error).toFixed(2)}%`;
    return `  ${String(m.carga).padStart(4)} cargas/s → p95 ${p95.padStart(10)} | errores ${err.padStart(7)} | n=${e.cargas}`;
  });
  const texto = [
    '',
    `=== Estrés front ${TARGET.toUpperCase()} (v${VERSION_ESPERADA}) ===`,
    ...filas,
    `bytes por página: ${reporte.bytes_por_pagina_promedio === null ? '-' : Math.round(reporte.bytes_por_pagina_promedio)}`,
    `versión inesperada: ${reporte.version_inesperada} | iteraciones descartadas: ${reporte.iteraciones_descartadas}`,
    `thresholds (escalón 200): ${ok ? 'OK' : 'FALLARON'}`,
    '',
  ].join('\n');

  return {
    stdout: texto,
    [`evidencias/reportes/estres-front-${TARGET}.json`]: JSON.stringify(reporte, null, 2),
  };
}
