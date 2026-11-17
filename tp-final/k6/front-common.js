import http from 'k6/http';

// Código compartido por los scripts del FRONT (canary y estrés).
// Se corren desde tp-final/:  k6 run k6/front-canary-split.js

export const FRONT = __ENV.FRONT_URL || 'http://terrasense.local';
// Qué versión es "la de siempre" y cuál "la nueva". Por env para reusar los
// mismos scripts en la demo de la v1.2.0 (VERSION_CANARY=1.2.0) o después de
// promover (VERSION_STABLE=1.1.0).
export const VERSION_STABLE = __ENV.VERSION_STABLE || '1.0.0';
export const VERSION_CANARY = __ENV.VERSION_CANARY || '1.1.0';

// Busca en el HTML los archivos que el navegador pediría después: src="/assets/..."
// o href="/assets/...". Así k6 imita a un navegador sin ser uno.
const RE_ASSETS = /(?:src|href)="(\/assets\/[^"]+)"/g;

function extraerAssets(body) {
  const rutas = [];
  if (typeof body !== 'string') return rutas;
  RE_ASSETS.lastIndex = 0; // la regex es global: reiniciar entre llamadas
  let m = RE_ASSETS.exec(body);
  while (m !== null) {
    rutas.push(m[1]);
    m = RE_ASSETS.exec(body);
  }
  return rutas;
}

// Bytes de la respuesta: Content-Length si nginx lo manda, si no el largo del body.
function bytesDe(r) {
  const cl = Number(r.headers['Content-Length']);
  if (Number.isFinite(cl) && cl > 0) return cl;
  return typeof r.body === 'string' ? r.body.length : 0;
}

// Carga UNA página completa como lo haría un visitante nuevo:
//  1) GET /  → lee X-App-Version (qué versión respondió el HTML)
//  2) pide todos los /assets/ que el HTML referencia, en la MISMA iteración
//     (y en paralelo, como el navegador)
// Un asset es "sano" si da 200 Y tiene la MISMA versión que el HTML. Si el
// HTML es 1.1.0 y el CSS vino de un pod 1.0.0 (o dio 404), es un asset roto:
// exactamente el problema de "assets mezclados" que la afinidad debe evitar.
export function cargarPagina(headers = {}, tags = {}) {
  // Cada iteración = visitante NUEVO: sin la cookie de afinidad de la vuelta
  // anterior. Si no la borráramos, el usuario virtual quedaría pegado a la
  // primera versión que le tocó y el % observado no reflejaría el peso.
  // Dentro de la iteración la cookie SÍ se mantiene (HTML → assets), que es
  // justamente lo que queremos probar.
  http.cookieJar().clear(FRONT);

  const html = http.get(`${FRONT}/`, {
    headers,
    tags: Object.assign({ recurso: 'html' }, tags),
  });
  const version = html.headers['X-App-Version'] || null;
  const rutas = html.status === 200 ? extraerAssets(html.body) : [];

  let assetsRotos = 0;
  let maxAsset = 0;
  let bytes = bytesDe(html);
  const rotos = [];

  if (rutas.length > 0) {
    const resps = http.batch(rutas.map((ruta) => ({
      method: 'GET',
      url: `${FRONT}${ruta}`,
      params: { headers, tags: Object.assign({ recurso: 'asset' }, tags) },
    })));
    resps.forEach((r, i) => {
      bytes += bytesDe(r);
      maxAsset = Math.max(maxAsset, r.timings.duration);
      const vAsset = r.headers['X-App-Version'] || null;
      if (r.status !== 200 || vAsset !== version) {
        assetsRotos++;
        rotos.push(`${rutas[i]} status=${r.status} v=${vAsset} (html v=${version})`);
      }
    });
  }

  return {
    html,
    version,
    ok: html.status === 200,
    // Duración del HTML solo (lo que mide un chequeo HTTP simple).
    duracionHtml: html.timings.duration,
    // Duración de la página: HTML + el asset más lento (se piden en paralelo).
    // Es más parecido a lo que espera el usuario.
    duracionPagina: html.timings.duration + maxAsset,
    assets: rutas.length,
    assetsRotos,
    rotos,
    bytes,
  };
}
