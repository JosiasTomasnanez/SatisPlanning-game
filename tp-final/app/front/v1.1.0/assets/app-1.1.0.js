// Canary 1.1.0: MISMO comportamiento que la 1.0.0 (polling cada 2 s a la API)
// para que la comparación stable vs canary sea justa; solo cambia la UI.
'use strict';

const API = 'http://api.terrasense.local';
const estado = document.getElementById('estado');
const tarjetas = document.getElementById('tarjetas');

// Pide un endpoint con timeout de 5 s: si la API no responde, preferimos
// mostrar un error a dejar la pantalla "colgada".
async function pedir(ruta, signal) {
  const r = await fetch(API + ruta, { signal });
  if (!r.ok) throw new Error('HTTP ' + r.status);
  return r;
}

// Arma cada tarjeta con textContent (no innerHTML): los datos vienen de los
// sensores y no deben poder inyectar HTML/JS en la página (XSS).
function crearTarjeta(l) {
  const div = document.createElement('div');
  div.className = 'tarjeta';
  const campos = [
    ['h2', l.sensor_id],
    ['p', 'Temp: ' + (+l.temperatura).toFixed(1) + ' °C'],
    ['p', 'H. suelo: ' + (+l.humedad_suelo).toFixed(1) + ' %'],
    ['p', 'H. aire: ' + (+l.humedad_aire).toFixed(1) + ' %'],
    ['small', new Date(l.ts).toLocaleString()],
  ];
  for (const [tag, texto] of campos) {
    const el = document.createElement(tag);
    el.textContent = texto;
    div.appendChild(el);
  }
  return div;
}

async function refrescar() {
  const ctrl = new AbortController();
  const t = setTimeout(() => ctrl.abort(), 5000);
  try {
    const [rLect, rStats] = await Promise.all([
      pedir('/api/sensores', ctrl.signal),
      pedir('/api/stats', ctrl.signal),
    ]);
    const lect = await rLect.json();
    const stats = await rStats.json();
    document.getElementById('total').textContent = stats.total;
    document.getElementById('pod').textContent = stats.pod;
    // Se puede leer gracias a exposedHeaders en el CORS del back.
    document.getElementById('version-back').textContent = rStats.headers.get('X-App-Version') || '?';
    tarjetas.replaceChildren(...lect.map(crearTarjeta));
    estado.className = 'ok';
    estado.textContent = 'Sistema operativo';
  } catch (e) {
    estado.className = 'error';
    estado.textContent = 'No se pudo contactar al servidor (' + e.message + '). Reintentando...';
  } finally {
    clearTimeout(t);
  }
}

refrescar();
setInterval(refrescar, 2000);
