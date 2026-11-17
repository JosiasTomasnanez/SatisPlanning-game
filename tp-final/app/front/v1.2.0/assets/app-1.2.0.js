// v1.2.0 — BUG INTENCIONAL para la demo de rollback.
// Simula un error real: el código espera una configuración global que en este
// release nadie define (se olvidó en el deploy). Leer una propiedad de
// undefined lanza TypeError, el script se corta antes de dibujar nada y el
// usuario ve una pantalla en blanco.
// Desde el servidor todo "anda": el HTML y este JS responden 200. Solo un
// chequeo con navegador real (k6/browser) detecta la falla.
'use strict';

const config = window.__TERRASENSE_CONFIG__; // undefined: nunca se carga

// TypeError: Cannot read properties of undefined (reading 'api')
const API = config.api.baseUrl;

// Este código nunca llega a ejecutarse.
document.getElementById('app').textContent = 'TerraSense — API: ' + API;
