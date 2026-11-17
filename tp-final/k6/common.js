import http from 'k6/http';
import { check } from 'k6';

// Código compartido por todos los scripts de carga del back (línea base TP3).
// Se ejecutan desde la carpeta tp-final/:  k6 run k6/load.js

// La URL se puede cambiar por env para reusar los scripts en otro entorno.
export const BASE = __ENV.BASE_URL || 'http://api.terrasense.local';

// Simula UN reporte de un sensor ESP32. El sensor_id es aleatorio entre 2000
// para que los datos se parezcan a una flota real y no a un único sensor.
export function reportar() {
  const payload = JSON.stringify({
    sensor_id: `esp32-${Math.floor(Math.random() * 2000)}`,
    temperatura: 15 + Math.random() * 20,
    humedad_suelo: 20 + Math.random() * 60,
    humedad_aire: 30 + Math.random() * 60,
  });
  const res = http.post(`${BASE}/api/sensores`, payload, {
    headers: { 'Content-Type': 'application/json' },
    // Tag "name": permite poner thresholds solo sobre este endpoint.
    tags: { name: 'POST_sensores' },
  });
  check(res, { 'status 201': (r) => r.status === 201 });
  return res;
}

// Los SLOs del TP3 escritos como thresholds: si no se cumplen, k6 termina con
// código de error (sirve para automatizar la decisión pasa / no pasa).
export const thresholds = {
  http_req_failed: ['rate<0.01'],                       // < 1% de errores
  'http_req_duration{name:POST_sensores}': ['p(95)<300'], // p95 < 300 ms
};
