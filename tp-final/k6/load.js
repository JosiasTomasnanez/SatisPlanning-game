import { reportar, thresholds } from './common.js';

// LOAD (carga nominal): 2000 sensores x 1 reporte cada 30 s ~= 67 req/s.
// constant-arrival-rate: k6 mantiene 67 req/s aunque el sistema se ponga lento
// (modelo "abierto", como sensores reales que no esperan a nadie). Con un
// número fijo de usuarios, si el back se pone lento bajaría la carga y el
// problema quedaría oculto.
export const options = {
  scenarios: {
    flota: {
      executor: 'constant-arrival-rate',
      rate: 67,
      timeUnit: '1s',
      duration: '5m',
      preAllocatedVUs: 50,
      maxVUs: 300,
    },
  },
  thresholds,
};

export default function () {
  reportar();
}
