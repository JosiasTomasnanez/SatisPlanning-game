import { reportar } from './common.js';

// STRESS: escalones crecientes (100 -> 1200 req/s) para encontrar el punto de
// quiebre del back y ver cómo reacciona el HPA. No esperamos que "pase":
// buscamos DÓNDE deja de cumplir el SLO.
export const options = {
  scenarios: {
    rampa: {
      executor: 'ramping-arrival-rate',
      startRate: 50,
      timeUnit: '1s',
      preAllocatedVUs: 100,
      maxVUs: 1500,
      stages: [
        { target: 100, duration: '1m' },
        { target: 200, duration: '2m' },
        { target: 400, duration: '2m' },
        { target: 800, duration: '2m' },
        { target: 1200, duration: '2m' },
        { target: 0, duration: '1m' },
      ],
    },
  },
  thresholds: {
    // abortOnFail: si los errores superan el 10% (evaluado tras 30 s de
    // margen) cortamos: ya encontramos el quiebre y seguir solo satura la PC.
    http_req_failed: [{ threshold: 'rate<0.10', abortOnFail: true, delayAbortEval: '30s' }],
    'http_req_duration{name:POST_sensores}': ['p(95)<300'],
  },
};

export default function () {
  reportar();
}
