import http from 'k6/http';
import { check } from 'k6';
import { BASE, reportar } from './common.js';

// E2 (SPIKE): pico casi vertical de 20 a 1500 req/s en 5 s.
// MODE=cpu (default): mitad escrituras, mitad /api/debug/burn -> satura CPU y
//   muestra si el HPA llega a tiempo.
// MODE=oom: /api/debug/leak retiene memoria -> los pods superan el limit,
//   K8s los mata (OOMKilled) y los reinicia; medimos la recuperación.
const MODE = __ENV.MODE || 'cpu';

export const options = {
  scenarios: {
    spike: {
      executor: 'ramping-arrival-rate',
      startRate: 20,
      timeUnit: '1s',
      preAllocatedVUs: 500,
      maxVUs: 3000,
      stages: [
        { target: 20, duration: '30s' },    // calma (referencia)
        { target: 1500, duration: '5s' },   // pico casi vertical
        { target: 1500, duration: '2m' },   // sostenido
        { target: 20, duration: '10s' },    // vuelta a la calma
        { target: 20, duration: '2m' },     // observar recuperación
      ],
    },
  },
};

export default function () {
  if (MODE === 'oom') {
    const r = http.get(`${BASE}/api/debug/leak?mb=5`, { timeout: '10s' });
    check(r, { 'leak 200': (x) => x.status === 200 });
  } else if (Math.random() < 0.5) {
    const r = http.get(`${BASE}/api/debug/burn?ms=50`, { timeout: '10s' });
    check(r, { 'burn 200': (x) => x.status === 200 });
  } else {
    reportar();
  }
}
