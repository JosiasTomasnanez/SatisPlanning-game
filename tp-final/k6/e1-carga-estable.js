import http from 'k6/http';
import { Counter } from 'k6/metrics';
import { BASE } from './common.js';

// E1 (falla de un pod): carga estable de 40 req/s durante 90 s mientras, a
// mano, se borra un pod del back (kubectl delete pod ...).
// Cada error se loguea con timestamp para medir cuánto tarda el Service en
// dejar de mandar tráfico al pod muerto (ventana de errores).
const errores = new Counter('errores_e1');

export const options = {
  scenarios: {
    estable: {
      executor: 'constant-arrival-rate',
      rate: 40,
      timeUnit: '1s',
      duration: '90s',
      preAllocatedVUs: 50,
      maxVUs: 200,
    },
  },
};

export default function () {
  const r = http.post(
    `${BASE}/api/sensores`,
    JSON.stringify({ sensor_id: 'e1', temperatura: 20, humedad_suelo: 40, humedad_aire: 50 }),
    // timeout corto: un request colgado contra el pod muerto cuenta como error.
    { headers: { 'Content-Type': 'application/json' }, timeout: '5s' }
  );
  if (r.status !== 201) {
    errores.add(1);
    console.log(`ERR ${new Date().toISOString()} status=${r.status}`);
  }
}
