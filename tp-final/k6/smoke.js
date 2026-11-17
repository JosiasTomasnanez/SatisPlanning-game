import http from 'k6/http';
import { check, sleep } from 'k6';
import { BASE, reportar, thresholds } from './common.js';

// SMOKE: 1 usuario durante 30 s. No mide capacidad: verifica que el sistema
// "prende" (escribe y lee) antes de gastar tiempo en pruebas pesadas.
export const options = { vus: 1, duration: '30s', thresholds };

export default function () {
  reportar();
  const r = http.get(`${BASE}/api/sensores`);
  check(r, { 'GET 200': (x) => x.status === 200 });
  sleep(1);
}
