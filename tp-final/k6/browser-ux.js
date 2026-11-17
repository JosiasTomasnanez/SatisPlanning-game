import { browser } from 'k6/browser';

// E1 desde el punto de vista del USUARIO: un navegador real (Chromium) abre el
// front mientras se cae un pod del back. Los scripts HTTP miden el servidor;
// este mide lo que ve la persona (calidad en uso).
// Se toma un screenshot cada 5 s en evidencias/capturas/ (correr desde tp-final/).
export const options = {
  scenarios: {
    ux: {
      executor: 'shared-iterations',
      vus: 1,
      iterations: 1,
      options: { browser: { type: 'chromium' } },
    },
  },
};

const FRONT = __ENV.FRONT_URL || 'http://terrasense.local';
const DURACION_S = Number(__ENV.DURATION_S || 60);
const DIR = __ENV.CAPTURAS || 'evidencias/capturas';

export default async function () {
  const page = await browser.newPage();
  try {
    await page.goto(FRONT, { waitUntil: 'load' });
    const inicio = Date.now();
    let n = 0;
    while ((Date.now() - inicio) / 1000 < DURACION_S) {
      // #estado es el texto que el front actualiza en cada polling a la API.
      const estado = await page.locator('#estado').textContent();
      const t = Math.round((Date.now() - inicio) / 1000);
      console.log(`[t+${t}s] estado UI: ${estado}`);
      await page.screenshot({ path: `${DIR}/e1-ux-${String(n++).padStart(2, '0')}.png` });
      // waitForTimeout (y no sleep): sleep bloquea el event loop del navegador.
      await page.waitForTimeout(5000);
    }
  } finally {
    await page.close();
  }
}
