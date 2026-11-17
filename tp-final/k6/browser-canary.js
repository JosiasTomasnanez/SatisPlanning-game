import { browser } from 'k6/browser';
import { check } from 'k6';
import exec from 'k6/execution';
import { Counter, Rate } from 'k6/metrics';
import { VERSION_STABLE, VERSION_CANARY } from './front-common.js';

// NAVEGADOR REAL (Chromium) que visita el front N veces, cada vez como un
// usuario nuevo. Es el único chequeo que EJECUTA el JavaScript de la página:
// detecta la pantalla en blanco de la v1.2.0, que responde 200 en todo y
// que ni las probes ni k6 HTTP ven.
//
//   ETAPA=etapa-0 FORZAR_CANARY=1 N=3 k6 run k6/browser-canary.js
//
// FORZAR_CANARY=1 → agrega la cookie canary=always (el Ingress manda al canary
// aunque el peso sea 0). Así se prueba la versión nueva sin exponer usuarios.

const N = Number(__ENV.N || 20);
const FRONT = __ENV.FRONT_URL || 'http://terrasense.local';
const ETAPA = __ENV.ETAPA || 'manual';
const FORZAR = __ENV.FORZAR_CANARY === '1';
const DIR = __ENV.CAPTURAS || 'evidencias/capturas';
// Tiempo para que el JS haga el primer polling y dibuje los datos.
const ESPERA_MS = 2500;

const pantallaBlanca = new Rate('pantalla_blanca');
const vistasCanary = new Counter('browser_canary');
const vistasStable = new Counter('browser_stable');

export const options = {
  scenarios: {
    visitas: {
      // N visitas repartidas entre los VUs (con 1 VU, una tras otra).
      executor: 'shared-iterations',
      vus: 1,
      iterations: N,
      maxDuration: '10m',
      options: { browser: { type: 'chromium' } },
    },
  },
  thresholds: {
    // Tolerancia CERO: una sola pantalla en blanco ya es un incidente.
    pantalla_blanca: ['rate==0'],
  },
};

export default async function () {
  // Contexto nuevo = perfil de navegador limpio (sin cookies de afinidad de
  // la visita anterior): cada visita es un usuario distinto.
  const context = await browser.newContext();
  if (FORZAR) {
    await context.addCookies([{ name: 'canary', value: 'always', url: FRONT }]);
  }
  const page = await context.newPage();
  const nro = String(exec.scenario.iterationInTest + 1).padStart(2, '0');

  try {
    const resp = await page.goto(FRONT, { waitUntil: 'load', timeout: 15000 });
    await page.waitForTimeout(ESPERA_MS);

    // Marca de versión del DOM: qué versión RENDERIZÓ el navegador.
    const version = await page.evaluate(() => {
      const m = document.querySelector('meta[name="app-version"]');
      return m ? m.getAttribute('content') : 'sin-version';
    });
    // Pantalla en blanco = el body no tiene ningún texto visible.
    const texto = await page.evaluate(() => (document.body ? document.body.innerText.trim() : ''));
    const blanca = texto.length === 0;

    pantallaBlanca.add(blanca);
    if (version === VERSION_CANARY) vistasCanary.add(1);
    else if (version === VERSION_STABLE) vistasStable.add(1);

    check(resp, { 'HTML 200': (r) => r !== null && r.status() === 200 });
    check(blanca, { 'la página muestra contenido': (b) => !b });

    const sufijo = blanca ? '-BLANCA' : '';
    await page.screenshot({ path: `${DIR}/${ETAPA}-visita-${nro}-v${version}${sufijo}.png`, fullPage: true });
    // Hora en el log: permite cruzar cada captura con la bitácora y los videos.
    console.log(`${new Date().toISOString()} visita ${nro}: v${version}${blanca ? ' PANTALLA EN BLANCO' : ' OK'}`);
  } finally {
    await page.close();
    await context.close();
  }
}

export function handleSummary(data) {
  const m = (nombre, campo) => (data.metrics[nombre] ? data.metrics[nombre].values[campo] : 0);
  const reporte = {
    etapa: ETAPA,
    forzar_canary: FORZAR,
    visitas: N,
    vistas_canary: m('browser_canary', 'count'),
    vistas_stable: m('browser_stable', 'count'),
    pantallas_blancas: m('pantalla_blanca', 'passes'),
    generado: new Date().toISOString(),
  };
  const texto = `\n=== ${ETAPA} (navegador): ${reporte.visitas} visitas → canary ${reporte.vistas_canary}, `
    + `stable ${reporte.vistas_stable}, pantallas en blanco ${reporte.pantallas_blancas} ===\n`;
  return {
    stdout: texto,
    [`evidencias/reportes/${ETAPA}-browser.json`]: JSON.stringify(reporte, null, 2),
  };
}
