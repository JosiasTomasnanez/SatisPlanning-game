const express = require('express');
const cors = require('cors');
const { Pool } = require('pg');

const PORT = process.env.PORT || 3000;
// Versión de la app: viene del Deployment (env APP_VERSION) para que cada pod
// "diga" qué versión está corriendo sin tener que reconstruir la imagen.
const APP_VERSION = process.env.APP_VERSION || 'desconocida';

// Sin contraseña por defecto: antes había una escrita en el código, que es
// un hallazgo típico de SAST (Horusec). Ahora la credencial viene SOLO
// del Secret de Kubernetes; si falta, preferimos fallar al arrancar (fail fast)
// antes que conectarnos con un valor inventado.
if (!process.env.DB_PASSWORD) {
  console.error('Falta DB_PASSWORD (debe venir del Secret db-secret)');
  process.exit(1);
}

const pool = new Pool({
  host: process.env.DB_HOST || 'db',
  port: Number(process.env.DB_PORT || 5432),
  user: process.env.DB_USER || 'admin',
  password: process.env.DB_PASSWORD,
  database: process.env.DB_NAME || 'iot_db',
  max: Number(process.env.DB_POOL_MAX || 10),
  connectionTimeoutMillis: 5000,
});

const app = express();

// exposedHeaders: por defecto el navegador oculta los headers "no estándar" a
// JavaScript en peticiones CORS. Lo exponemos para que el front (otro origen:
// terrasense.local vs api.terrasense.local) pueda leer la versión del back.
app.use(cors({ exposedHeaders: ['X-App-Version'] }));

// Marca de versión en TODAS las respuestas: así k6, curl o el navegador pueden
// saber qué versión respondió cada request sin mirar logs.
app.use((_req, res, next) => {
  res.setHeader('X-App-Version', APP_VERSION);
  next();
});

app.use(express.json({ limit: '1mb' }));

let dbReady = false;

// Reintenta hasta que la DB esté disponible: en K8s el back puede arrancar
// antes que PostgreSQL, y no queremos que el pod muera por eso.
async function initDb() {
  for (;;) {
    try {
      await pool.query(`CREATE TABLE IF NOT EXISTS lecturas (
        id SERIAL PRIMARY KEY,
        sensor_id TEXT NOT NULL,
        temperatura REAL,
        humedad_suelo REAL,
        humedad_aire REAL,
        ts TIMESTAMPTZ NOT NULL DEFAULT now()
      )`);
      await pool.query('CREATE INDEX IF NOT EXISTS idx_lecturas_ts ON lecturas (ts DESC)');
      dbReady = true;
      console.log('DB lista');
      return;
    } catch (e) {
      console.error('DB no disponible, reintentando en 3s:', e.message);
      await new Promise((r) => setTimeout(r, 3000));
    }
  }
}

// Liveness: solo "el proceso responde" (si falla, K8s reinicia el pod).
// No consulta la DB a propósito: si la DB cae, reiniciar el back no arregla nada.
app.get('/healthz', (_req, res) => res.status(200).send('ok'));

// Readiness: "puedo atender tráfico" = además la DB responde.
// Si falla, K8s saca el pod del Service pero NO lo reinicia.
app.get('/readyz', async (_req, res) => {
  if (!dbReady) return res.status(503).send('db not ready');
  try {
    await pool.query('SELECT 1');
    return res.status(200).send('ready');
  } catch {
    return res.status(503).send('db error');
  }
});

// Endpoint de escritura (ESP32 / k6)
app.post('/api/sensores', async (req, res) => {
  const { sensor_id, temperatura, humedad_suelo, humedad_aire } = req.body || {};
  if (!sensor_id) return res.status(400).json({ error: 'sensor_id requerido' });
  try {
    // Consulta parametrizada ($1..$4): evita inyección SQL.
    await pool.query(
      'INSERT INTO lecturas (sensor_id, temperatura, humedad_suelo, humedad_aire) VALUES ($1,$2,$3,$4)',
      [sensor_id, temperatura, humedad_suelo, humedad_aire]
    );
    return res.status(201).json({ ok: true });
  } catch (e) {
    console.error(e.message);
    return res.status(500).json({ error: 'db error' });
  }
});

// Lecturas recientes (usado por el front)
app.get('/api/sensores', async (_req, res) => {
  try {
    const r = await pool.query('SELECT * FROM lecturas ORDER BY ts DESC LIMIT 20');
    return res.json(r.rows);
  } catch {
    return res.status(500).json({ error: 'db error' });
  }
});

// Devuelve también el nombre del pod: sirve para ver el balanceo entre réplicas.
app.get('/api/stats', async (_req, res) => {
  try {
    const r = await pool.query('SELECT count(*)::int AS total FROM lecturas');
    return res.json({ total: r.rows[0].total, pod: process.env.HOSTNAME, version: APP_VERSION });
  } catch {
    return res.status(500).json({ error: 'db error' });
  }
});

// ---- Endpoints de laboratorio para las pruebas de fallas (NO usar en producción) ----
// CPU: ocupa el event loop N ms para que el HPA vea uso de CPU. Ej: /api/debug/burn?ms=200
// El cálculo es determinístico a propósito: antes usaba Math.random(), que
// Horusec marca como generador débil (HS-JAVASCRIPT-6). Acá no hace falta
// azar, solo gastar CPU, así que se eliminó en vez de justificarlo.
app.get('/api/debug/burn', (req, res) => {
  const ms = Math.min(Number(req.query.ms || 100), 5000);
  const end = Date.now() + ms;
  let x = 0;
  while (Date.now() < end) { x = Math.sqrt(x + 1); }
  res.json({ burned_ms: ms, pod: process.env.HOSTNAME });
});

// Memoria: retiene N MB por request para provocar OOMKilled al superar limits.
const leak = [];
app.get('/api/debug/leak', (req, res) => {
  const mb = Math.min(Number(req.query.mb || 5), 100);
  leak.push(Buffer.alloc(mb * 1024 * 1024, 1));
  res.json({ retained_mb: leak.length * mb, pod: process.env.HOSTNAME });
});

app.listen(PORT, () => console.log(`back ${APP_VERSION} escuchando en ${PORT}`));
initDb();

// Cierre ordenado: K8s manda SIGTERM antes de matar el pod; cerramos el pool
// para no dejar conexiones colgadas en PostgreSQL.
process.on('SIGTERM', () => { pool.end().finally(() => process.exit(0)); });
