# RESUMEN — TP Final (apunte para la defensa)

Apunte de estudio, fase por fase: qué se hizo, para qué sirve, cómo se conecta
con lo anterior y cómo explicarlo en la presentación.

---

## 0. Organización del repositorio

```
main ──●──● 51c78a0 (código del juego SatisPlanning, no se toca)
             ├── tpSonarQube : TP de SonarQube (carpeta tpSonar/)
             └── tp-final    : este TP (carpeta tp-final/)
```

- La rama `tpSonarQube` se había creado desde la rama del TP1 (`feature/configurar-linter`)
  y no desde `main`, por eso arrastraba commits ajenos y estaba atrasada. Se rehízo
  desde `main` y se commiteó la carpeta `tpSonar/`.
- El TP Final se trabaja en la rama `tp-final`, creada desde `main` actualizado.
- Ramas de TPs anteriores: TP1 linters → `feature/configurar-linter`;
  TP2 Horusec → `dev` (workflow) y `TP2-Horusec` (análisis).

---

## Fase 1 — Línea base (TP3 rehecho)

### Qué se hizo
El TP3 (Kubernetes + HPA + k6 sobre TerraSense) se había hecho en otro repo y nunca
se ejecutó. Se integró en `tp-final/` como **línea base**: lo que medimos antes de
hacer cambios en el front, para tener contra qué comparar.

### El back (`app/back/server.js`)
| Cambio | Por qué |
|---|---|
| Header `X-App-Version` en toda respuesta (desde `APP_VERSION`) | Saber qué versión respondió cada request sin mirar logs |
| `cors({ exposedHeaders: ['X-App-Version'] })` | El navegador oculta headers no estándar a JS entre dominios distintos (front y API están en hosts distintos) |
| Se quitó la contraseña por defecto hardcodeada | Hallazgo típico de SAST (Horusec, TP2). Ahora viene solo del Secret; si falta, el back no arranca (*fail fast*) |

### Manifiestos (`k8s/base/`)
*Manifiesto*: archivo YAML que describe qué recurso querés que exista; Kubernetes se encarga de que exista.

| Archivo | Recurso | Para qué |
|---|---|---|
| 00-namespace | Namespace `terrasense` | Agrupar todo lo del proyecto |
| 01-config | ConfigMap + Secret | Configuración separada de la imagen; credenciales aparte |
| 02-db | StatefulSet PostgreSQL + PVC + Service `db` | DB con nombre fijo (`db-0`) y disco que sobrevive reinicios |
| 03-back | Deployment `back` (2 réplicas) + Service | El back, con imagen `terrasense-back:1.0.0` |
| 04-hpa | HorizontalPodAutoscaler | Escala el back de 2 a 8 pods según CPU (objetivo 60%) |

Definiciones rápidas:
- **Pod**: la unidad mínima que corre uno o más contenedores.
- **Deployment**: mantiene N réplicas iguales de un pod y gestiona las actualizaciones.
- **StatefulSet**: como un Deployment pero con identidad y disco estables (para bases de datos).
- **PVC** (PersistentVolumeClaim): pedido de disco persistente.
- **Service**: IP/nombre DNS estable que balancea entre los pods listos.
- **Tag explícito** (`1.0.0`, nunca `latest`): saber exactamente qué corre y poder volver atrás.
- **imagePullPolicy IfNotPresent**: usar la imagen construida dentro de Minikube sin ir a un registry.

### Probes
```
                 ┌──────────── readiness (/readyz, cada 3 s) ───────────┐
Kubernetes ──────┤  ¿podés atender? (incluye DB)  falla → sale del Service, NO se reinicia
                 └──────────── liveness (/healthz, cada 10 s) ──────────┐
                    ¿estás vivo?                  falla x3 → se REINICIA el pod
```
- La liveness no consulta la DB a propósito: si la DB se cae, reiniciar el back no arregla nada
  y provocaría reinicios en cadena.
- La liveness es más tolerante que la readiness para no matar un pod que solo está lento bajo carga.

### Requests, limits y HPA
- **requests**: lo que el pod reserva; el scheduler lo usa para ubicarlo.
- **limits**: el techo. Pasarse de memoria → **OOMKilled**; pasarse de CPU → *throttling* (lo frenan).
- El **HPA calcula el % sobre el request**: 60% de 100m = 60m. Sin request no hay base y el HPA no escala.
- Necesita **metrics-server** (addon de Minikube) para leer el consumo.
- Sube rápido (2 pods cada 15 s) y baja con calma (60 s) para no oscilar.

### Scripts de k6 (`k6/`, se corren desde `tp-final/`)
| Script | Carga | Qué mide |
|---|---|---|
| smoke | 1 usuario, 30 s | Que el sistema funcione (escribe y lee) |
| load | 67 req/s, 5 min | Carga nominal: 2000 sensores / 30 s |
| stress | escalones 100 → 1200 req/s | Punto de quiebre del back y reacción del HPA |
| e1-carga-estable | 40 req/s, 90 s + borrar un pod a mano | Ventana de errores hasta que el Service saca el pod muerto |
| spike | 20 → 1500 req/s en 5 s | `MODE=cpu`: CPU y HPA; `MODE=oom`: memoria → OOMKilled y recuperación |
| browser-ux | navegador real, captura cada 5 s | Lo que ve el usuario durante la falla (calidad en uso) |

- **constant-arrival-rate / ramping-arrival-rate** (modelo abierto): k6 mantiene la tasa de
  requests aunque el sistema se ponga lento, como sensores reales que no esperan a nadie.
- **threshold**: SLO escrito como condición; si no se cumple, k6 termina con error.
  Base: errores < 1% y p95 < 300 ms.
- **p95**: el 95% de los requests tardó menos que este valor.

### Frase para la presentación
> "Rehicimos el TP3 en este repo como línea base: el back corre en Kubernetes con probes que
> lo recuperan solo y un HPA que escala por CPU, y con k6 medimos su capacidad antes de tocar el front."

### Posibles preguntas
- *¿Por qué StatefulSet para la DB?* Identidad y disco estables; un Deployment trata los pods como intercambiables.
- *¿Qué pasa si se borra el Secret?* El back no arranca: no hay contraseña por defecto, a propósito.
- *¿Por qué el selector del Deployment no incluye `version`?* El selector es inmutable; con la
  versión adentro no se podría actualizar sin recrear el Deployment.
- *¿El Secret es seguro?* Está en base64, no cifrado. En producción usaríamos Vault o Sealed
  Secrets y no lo versionaríamos; acá es un laboratorio.

---

## Fase 2 — Front versionado (1.0.0 / 1.1.0 / 1.2.0)

### Qué se hizo
Un **único Dockerfile** construye las tres versiones del front. Solo cambian dos
argumentos de build: `APP_VERSION` y la carpeta de origen `SRC` (por defecto `v<versión>`).

```
app/front/
├── Dockerfile      ← uno solo para todas las versiones
├── nginx.conf      ← plantilla con __APP_VERSION__
├── v1.0.0/         ← stable: el index.html del TP3 sin cambios
├── v1.1.0/         ← canary: cambio visual exagerado, CSS/JS en /assets/
└── v1.2.0/         ← rota a propósito: pantalla en blanco con HTTP 200
```

Build: `docker build --build-arg APP_VERSION=1.1.0 -t terrasense-front:1.1.0 .`
(tags explícitos `terrasense-front:1.0.0 / 1.1.0 / 1.2.0`, nunca `latest`).

### Dockerfile: decisiones
- Base `nginx-unprivileged`: nginx corre como usuario 101 (no root) y escucha en 8080.
- `USER root` solo durante el build para modificar archivos, y se vuelve a `USER 101`.
  Principio de **mínimo privilegio**: en ejecución nunca es root.
- **ARG**: variable que existe solo durante el build (no queda en el contenedor).

### Las 3 marcas de versión
| Marca | Dónde | Quién la usa |
|---|---|---|
| `<meta name="app-version">` | Dentro del HTML (DOM) | El navegador / k6 browser: confirma qué versión **renderizó** el usuario |
| `/version.txt` | Archivo liviano | Probes de K8s y conteo con `curl` (qué % va a canary) |
| Header `X-App-Version` | En **toda** respuesta de nginx (incluso 404) | k6 HTTP: detectar assets de otra versión (HTML 1.1.0 + CSS de 1.0.0) |

Hacen falta las tres porque cada una responde una pregunta distinta: el header dice
quién respondió **cada request**, el meta dice qué **vio** el usuario, y version.txt es
la forma **más barata** de preguntarle a un pod su versión.

### nginx.conf: decisiones
- `add_header ... always`: el header sale también en errores (ahí es cuando más importa).
- `Cache-Control: no-store`: sin caché, para que nadie vea una versión vieja guardada
  y para que las mediciones del canary no se falseen.
- `location /assets/ { try_files $uri =404; }`: un asset que no existe da **404 visible**.
  Si cayera en index.html daría 200 con HTML adentro y el error quedaría oculto.
- `location / { try_files $uri $uri/ /index.html; }`: fallback típico de SPA.

### Problema de "assets mezclados"
```
Usuario ─ GET /                    → Ingress → pod CANARY → HTML 1.1.0 (pide app-1.1.0.css)
        ─ GET /assets/app-1.1.0.css → Ingress → pod STABLE → 404 (no lo tiene)
                                                   ⇒ página rota a medias
```
Por eso la v1.1.0 tiene CSS/JS externos con la versión en el nombre: para que el
problema se pueda demostrar. La solución es la **afinidad por cookie** (Fase 3): el
mismo usuario siempre va al mismo grupo de pods.

### Las versiones
- **1.0.0 (stable)**: tabla clásica, polling a la API cada 2 s.
- **1.1.0 (canary)**: **mismo comportamiento** (polling 2 s a `/api/sensores` y `/api/stats`),
  pero fondo verde #39ff14, banner fijo "ESTÁS VIENDO LA VERSIÓN CANARY 1.1.0", letra
  monoespaciada y tarjetas. Exagerado para que en un video se distinga sin dudas.
  Además muestra la versión del back (header leído gracias al CORS de la Fase 1) y arma
  el DOM con `textContent` (no `innerHTML`) para evitar XSS.
- **1.2.0 (rota)**: el HTML solo tiene `<div id="app">` y un JS que lee
  `config.api.baseUrl` con `config` undefined → **TypeError** → no se dibuja nada.

### ¿Por qué un chequeo HTTP no detecta la v1.2.0?
```
curl /                     → 200 OK, HTML válido      ✔
curl /assets/app-1.2.0.js  → 200 OK, JS existe        ✔
curl /version.txt          → 200 "1.2.0"              ✔  ← las probes dan OK
Navegador: ejecuta el JS   → TypeError → body vacío   ✘  ← el usuario ve pantalla en blanco
```
El servidor entrega todo bien; el error ocurre **en el navegador** al ejecutar el JS.
Ni las probes ni k6 HTTP ejecutan JavaScript. Solo un navegador real (k6/browser,
Fase 4) lo detecta, midiendo si `body.innerText` está vacío.
Es lo que pasó en el incidente de la madrugada de helada: monitoreo en verde y usuarios sin ver nada.

### Frase para la presentación
> "Las tres versiones salen del mismo Dockerfile y llevan su versión en tres lugares:
> header, meta y version.txt. La 1.2.0 está rota a propósito: devuelve 200 en todo, pero
> deja la pantalla en blanco; eso demuestra que un health check HTTP no alcanza y que
> necesitamos un navegador real en el canary."

### Posibles preguntas
- *¿Por qué no usar `latest`?* No se sabe qué versión corre, no hay rollback a algo
  conocido, y con `latest` K8s fuerza `imagePullPolicy: Always`.
- *¿Por qué tres versiones?* 1.0.0 = lo que hay en producción; 1.1.0 = el cambio a
  validar (debería pasar); 1.2.0 = prueba de que el proceso **frena** un release malo.
- *¿El 404 de assets no es peor para el usuario?* Es peor ocultarlo: con 200 y HTML
  adentro el error no aparece en ninguna métrica. Con 404 lo detecta k6 (`assets_rotos`).
