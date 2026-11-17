import { Counter, Trend, Rate } from 'k6/metrics';
import { cargarPagina, VERSION_STABLE, VERSION_CANARY } from './front-common.js';

// ¿El reparto stable/canary es el que configuramos, y el canary anda tan bien
// como la stable? Se corre en cada etapa del rollout (peso 10, 25, 50, 100).
//
//   ETAPA=peso-10 PESO=10 k6 run k6/front-canary-split.js
//
// Llegan visitantes nuevos a ritmo constante (RATE por segundo) durante
// DURATION, SIN header ni cookie de canary: es tráfico "como el de un usuario
// real", que el Ingress reparte por peso.

const RATE = Number(__ENV.RATE || 20);
const DURATION = __ENV.DURATION || '5m';
const ETAPA = __ENV.ETAPA || 'manual';
const PESO = Number(__ENV.PESO || 0);

// Cuántas visitas cayeron en cada versión (para calcular el % observado).
const visitasCanary = new Counter('visitas_canary');
const visitasStable = new Counter('visitas_stable');
// Respuestas sin versión reconocible (ej. un 502 del Ingress, que no lo
// genera nginx del front): no se pueden atribuir a ninguna versión.
const visitasSinVersion = new Counter('visitas_sin_version');

// Latencia del HTML solo, por versión.
const latCanary = new Trend('lat_canary', true);
const latStable = new Trend('lat_stable', true);
// Carga de página completa (HTML + assets), por versión.
const paginaCanary = new Trend('pagina_canary', true);
const paginaStable = new Trend('pagina_stable', true);
// Tasa de errores por versión, y assets rotos (404 o de otra versión).
const errCanary = new Rate('err_canary');
const errStable = new Rate('err_stable');
const assetsRotos = new Rate('assets_rotos');

export const options = {
  scenarios: {
    visitantes: {
      // Modelo abierto: llegan RATE visitas/s aunque el sistema se ponga
      // lento (los usuarios reales no esperan a que el servidor se recupere).
      executor: 'constant-arrival-rate',
      rate: RATE,
      timeUnit: '1s',
      duration: DURATION,
      preAllocatedVUs: Math.max(10, RATE),
      maxVUs: Math.max(100, RATE * 10),
    },
  },
  // Criterios para AVANZAR de etapa, fijados de antemano. Si alguno falla,
  // k6 termina con código 99 y rollout.sh hace rollback.
  thresholds: {
    http_req_failed: ['rate<0.01'],     // < 1% de requests fallidos en total
    err_canary: ['rate<0.01'],          // < 1% de errores en el canary
    lat_canary: ['p(95)<300'],          // p95 del HTML canary < 300 ms
    assets_rotos: ['rate<0.01'],        // < 1% de assets mezclados o 404
  },
};

export default function () {
  const p = cargarPagina();

  if (p.version === VERSION_CANARY) {
    visitasCanary.add(1);
    latCanary.add(p.duracionHtml);
    paginaCanary.add(p.duracionPagina);
    errCanary.add(!p.ok);
  } else if (p.version === VERSION_STABLE) {
    visitasStable.add(1);
    latStable.add(p.duracionHtml);
    paginaStable.add(p.duracionPagina);
    errStable.add(!p.ok);
  } else {
    visitasSinVersion.add(1);
  }

  // Se registra cada asset (true = roto) para que la tasa sea "por asset".
  for (let i = 0; i < p.assets; i++) assetsRotos.add(i < p.assetsRotos);
  if (p.assetsRotos > 0) console.warn(`ASSET ROTO ${new Date().toISOString()} ${p.rotos.join(' | ')}`);
}

// ---- Reporte de evidencia ----
function valor(data, metrica, campo) {
  const m = data.metrics[metrica];
  return m && m.values[campo] !== undefined ? m.values[campo] : 0;
}

function thresholdsOk(data) {
  return Object.values(data.metrics).every((m) =>
    !m.thresholds || Object.values(m.thresholds).every((t) => t.ok));
}

export function handleSummary(data) {
  const canary = valor(data, 'visitas_canary', 'count');
  const stable = valor(data, 'visitas_stable', 'count');
  const sinVersion = valor(data, 'visitas_sin_version', 'count');
  const total = canary + stable + sinVersion;
  const pctCanary = total > 0 ? (100 * canary) / total : 0;

  const reporte = {
    etapa: ETAPA,
    peso_configurado: PESO,
    porcentaje_canary_observado: Number(pctCanary.toFixed(2)),
    visitas: { total, canary, stable, sin_version: sinVersion },
    version_stable: VERSION_STABLE,
    version_canary: VERSION_CANARY,
    p95_ms: {
      html_canary: valor(data, 'lat_canary', 'p(95)'),
      html_stable: valor(data, 'lat_stable', 'p(95)'),
      pagina_canary: valor(data, 'pagina_canary', 'p(95)'),
      pagina_stable: valor(data, 'pagina_stable', 'p(95)'),
    },
    tasa_error: {
      http_total: valor(data, 'http_req_failed', 'rate'),
      canary: valor(data, 'err_canary', 'rate'),
      stable: valor(data, 'err_stable', 'rate'),
    },
    assets_rotos: {
      tasa: valor(data, 'assets_rotos', 'rate'),
      cantidad: valor(data, 'assets_rotos', 'passes'),
    },
    thresholds_ok: thresholdsOk(data),
    rate_por_segundo: RATE,
    duracion: DURATION,
    generado: new Date().toISOString(),
  };

  // Resumen corto y en español para la terminal (queda legible en el video).
  const r = reporte;
  const texto = [
    '',
    `=== ${r.etapa}: peso configurado ${r.peso_configurado}% → canary observado ${r.porcentaje_canary_observado}% ===`,
    `visitas: ${r.visitas.total} (canary ${canary}, stable ${stable}, sin versión ${sinVersion})`,
    `p95 HTML    canary ${r.p95_ms.html_canary.toFixed(1)} ms | stable ${r.p95_ms.html_stable.toFixed(1)} ms`,
    `p95 página  canary ${r.p95_ms.pagina_canary.toFixed(1)} ms | stable ${r.p95_ms.pagina_stable.toFixed(1)} ms`,
    `errores     canary ${(100 * r.tasa_error.canary).toFixed(2)}% | stable ${(100 * r.tasa_error.stable).toFixed(2)}%`,
    `assets rotos: ${r.assets_rotos.cantidad} (${(100 * r.assets_rotos.tasa).toFixed(2)}%)`,
    `thresholds: ${r.thresholds_ok ? 'OK' : 'FALLARON'}`,
    '',
  ].join('\n');

  return {
    stdout: texto,
    [`evidencias/reportes/${ETAPA}-split.json`]: JSON.stringify(reporte, null, 2),
  };
}
