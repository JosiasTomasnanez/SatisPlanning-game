# RESUMEN — TP Final (apunte para la defensa)

Apunte de estudio, fase por fase: qué se hizo, para qué sirve, cómo se conecta
con lo anterior y cómo explicarlo en la presentación.

**Cómo leer este apunte:** primero leé "El TP en 2 minutos" (el mapa). Después cada
fase arranca con **En pocas palabras** (qué problema resuelve) y recién ahí viene el detalle.

---

## ★ El TP en 2 minutos (leer esto primero)

### La historia
TerraSense es una empresa con sensores en el campo que mandan temperatura y humedad a
un servidor (**back**). Los dueños miran esos datos en una página web (**front**).

Una madrugada de helada subieron una versión nueva del front que dejaba **la pantalla en
blanco**. El monitoreo decía "todo OK" (el servidor respondía), pero nadie podía ver los
datos justo cuando más importaban.

**La pregunta del TP:** ¿cómo sacamos una versión nueva sin que pueda volver a pasar eso?

### La respuesta: canary release
La versión nueva se despliega **junto** a la actual y recibe solo un porcentaje del
tráfico real. En cada porcentaje se mide (errores, latencia, pantalla en blanco). Si los
números cumplen los criterios fijados de antemano, se sube el porcentaje; si no, se vuelve
a 0% (rollback) y el problema afectó solo a ese porcentaje de usuarios, durante poco tiempo.

```
 Versión actual (1.0.0) ─┐
                         ├─► Ingress Controller (decide qué versión recibe cada request) ─► usuarios
 Versión nueva  (1.1.0) ─┘     10% → 25% → 50% → 100%   (si algo falla → 0%)
```

### Las piezas, en una línea cada una
| Pieza | Qué hace | Fase |
|---|---|---|
| Back + base de datos en Kubernetes | El servidor, que se reinicia solo si se cae y agrega réplicas si hay mucha carga | 1 (era el TP3) |
| k6 de carga | Genera tráfico de sensores y mide cuánto aguanta el back antes de cambiar nada (línea base) | 1 |
| Tres versiones del front | 1.0.0 = la actual; 1.1.0 = la nueva (verde, para que se note); 1.2.0 = **rota a propósito** | 2 |
| Stable + canary + Ingress | Las dos versiones corriendo juntas y el Ingress repartiendo el tráfico entre ellas | 3 |
| k6 del canary y de estrés | Miden qué versión recibió cada visita, latencia, errores y si la pantalla quedó en blanco | 4 |
| Scripts (rollout.sh) | Automatizan el plan: suben el % solo si las mediciones cumplen; si no, rollback a 0 | 5 |
| CI (GitHub Actions) | Corre linters y Horusec sobre el código; si fallan, no se construyen las imágenes | 6 |
| Informe + ISO 25000 | Qué característica de calidad mide cada prueba y qué queda sin medir | 7 |

### Las 3 cosas que tenés que poder decir sí o sí
1. **Un "200 OK" no significa que el usuario ve la página.** La v1.2.0 responde 200 en todo
   y deja la pantalla en blanco. Por eso usamos un **navegador real** (k6/browser) en el canary.
2. **El canary expone la versión nueva de a poco y con criterios escritos antes.** Se avanza
   solo si los números dan bien; si no, se vuelve a 0% en segundos (rollback).
3. **Cada prueba mide una característica de calidad de ISO/IEC 25010** (rendimiento,
   fiabilidad, seguridad...), y sabemos cuáles quedaron sin cubrir.

### Recorrido de la demo
```
CI en verde → deploy en Minikube → línea base (k6 al back) → canary 0% con cookie
→ 10 → 25 → 50 → 100 (avanza solo si da OK) → promoción
→ demo con v1.2.0: el navegador ve pantalla en blanco → rollback automático a 0%
→ estrés A/B: ¿la nueva aguanta igual que la vieja? → veredicto go / no-go
```

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

### Relación entre el juego (SatisPlanning) y TerraSense
**No hay relación técnica entre las dos aplicaciones; solo comparten el repositorio.**
```
Repo Calidad_software
├── main: juego SatisPlanning (Python + pygame), proyecto de Ingeniería de Software
│     ├── TP1: Ruff + Pylint analizando el código del JUEGO
│     └── TP2: Horusec (SAST) analizando el código del JUEGO
└── tp-final: TerraSense (Node.js + nginx + PostgreSQL en Kubernetes)
      ├── TP3 (línea base): k8s + HPA + k6 sobre TERRASENSE
      └── TP Final: canary + estrés + ISO 25000 sobre TERRASENSE
```
- TP1 y TP2 usaron el juego como código sobre el cual aplicar **análisis estático**.
- Desde el TP3 la consigna cambia de sistema: TerraSense es una app web cliente-servidor,
  que se puede desplegar en Kubernetes y someter a carga; el juego es una app de escritorio.
- Lo que se reutiliza de TP1 y TP2 son **las herramientas, no el código**: en la Fase 6 el
  pipeline de CI corre linters y Horusec sobre el código de TerraSense, como quality gate
  antes de construir las imágenes.
- Frase: *"TP1 y TP2 aplicaron análisis estático a un proyecto Python; en el final esas mismas
  herramientas son la primera quality gate del pipeline de TerraSense."*

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

---

## Fase 3 — Canary en Kubernetes (LA PARTE MÁS IMPORTANTE)

### Qué es un canary
**Canary release**: desplegar la versión nueva **al lado** de la vieja y mandarle solo
una parte del tráfico real. Se miden métricas y, si están bien, se sube el porcentaje
de a poco; si están mal, se vuelve a 0% (**rollback**) y el impacto queda acotado a ese porcentaje.

Diferencias con otras estrategias:
| Estrategia | Cómo funciona | Riesgo |
|---|---|---|
| Recreate | Bajo todo y subo la nueva | Corte de servicio |
| Rolling update (default de K8s) | Reemplaza pods de a uno | Todos terminan en la nueva; no se elige **quién** la ve |
| Blue/Green | Dos entornos completos, switch 0% → 100% | Todo o nada |
| **Canary** | Las dos versiones conviven, % controlado | Exposición **gradual y medible** |

### Archivos
| Archivo | Recurso | Clave |
|---|---|---|
| `k8s/stable/deployment.yaml` | Deployment `front-stable` | 1.0.0, 2 réplicas, `track: stable` |
| `k8s/stable/service.yaml` | Service `front-stable` | selecciona `app: front` + `track: stable` |
| `k8s/canary/deployment.yaml` | Deployment `front-canary` | 1.1.0, 1 réplica, `track: canary`, **mismos recursos y probes** |
| `k8s/canary/service.yaml` | Service `front-canary` | selecciona `app: front` + `track: canary` |
| `k8s/ingress.yaml` | 2 Ingress: API y front principal | API sin afinidad; front con afinidad por cookie |
| `k8s/canary/ingress-canary.yaml` | Ingress canary | `canary: "true"`, peso 0, cookie `canary`, header `X-Canary` |

Definiciones rápidas:
- **Ingress**: regla de ruteo HTTP (host + path → Service).
- **Ingress Controller** (ingress-nginx): el nginx que lee esas reglas y realmente enruta.
  Es quien implementa el canary, no Kubernetes.
- **Label**: etiqueta clave=valor en un recurso. **Selector**: filtro por labels
  (así un Service sabe qué pods le corresponden).
- **track**: label que inventamos para separar stable/canary.

### El flujo completo
```
                      terrasense.local
Navegador ──────────► INGRESS CONTROLLER (ingress-nginx)
                       │  Ingress principal: terrasense-ingress → front-stable
                       │  Ingress canary:    terrasense-ingress-canary → front-canary
                       │
                       │  ¿header X-Canary?  always → CANARY / never → STABLE
                       │        └─ no ─► ¿cookie canary?  always → CANARY / never → STABLE
                       │                       └─ no ─► ¿cookie de afinidad? → mismo grupo/pod de antes
                       │                                     └─ no ─► sorteo por PESO (ej. 10%)
                       ▼                                            ▼
            Service front-stable                        Service front-canary
            (app=front, track=stable)                   (app=front, track=canary)
              ├─ pod 1.0.0                                └─ pod 1.1.0
              └─ pod 1.0.0

                      api.terrasense.local
Navegador ──────────► Ingress terrasense-ingress-api (SIN afinidad, SIN canary) ─► Service back ─► pods back (HPA 2..8)
```

### Precedencia: header → cookie → peso
1. **Header `X-Canary`** (`always`/`never`): lo usan k6 y QA para forzar una versión.
   El estrés A/B lo usa: `never` = medir solo la stable, `always` = medir solo el canary.
2. **Cookie `canary`** (`always`/`never`): sirve desde el navegador (no se pueden poner
   headers fácilmente). Con `canary=always` en la etapa 0 el equipo prueba el canary
   **con peso 0**, es decir, sin exponer a ningún usuario real.
3. **Peso**: el resto del tráfico se sortea. `canary-weight: "10"` ≈ 10% de los requests
   **nuevos** al canary.

Cualquier otro valor del header o cookie se ignora y pasa al paso siguiente.

### Afinidad por cookie (sesión pegajosa)
- Sin afinidad, **cada request** se sortea por separado: el HTML podría venir del canary
  y el CSS del stable → `/assets/app-1.1.0.css` da 404 → página rota (assets mezclados).
- Con `affinity: cookie`, el controller entrega la cookie `terrasense-front` y los
  siguientes requests de ese navegador van al **mismo pod**.
- `affinity-canary-behavior: sticky`: si caíste en el canary, seguís en el canary.
- En el Ingress canary **hay que repetir** las anotaciones de afinidad: el controller
  ignora las demás anotaciones del canary (las hereda del principal), pero no las de afinidad.

### ¿Por qué la API va en otro Ingress?
1. **Afinidad**: el front la **necesita**; la API **no la quiere**. k6 guarda cookies por
   usuario virtual; con afinidad cada VU quedaría pegado a un pod del back, los pods
   nuevos que crea el HPA casi no recibirían carga y el escalado se mediría mal.
2. **Aislamiento**: el canary es **solo del front**. Así un cambio de peso nunca toca la
   API y, si algo sale mal en el canary, el back no se entera.
3. Cada Ingress tiene sus propias anotaciones (ej. `proxy-body-size: 1m` solo en la API).

### "Peso 100 NO es promoción"
Con peso 100, el 100% del tráfico va al canary, pero:
- El Deployment **stable sigue con la 1.0.0**: "producción", según lo declarado, sigue siendo la vieja.
- Todo el tráfico cae en **1 pod** canary (la stable tiene 2): menos capacidad y sin redundancia.
- Si alguien borra el Ingress canary, o lo pone en peso 0, o manda `X-Canary: never`,
  vuelve la 1.0.0 sin que nadie lo haya decidido.

**Promover** = la stable pasa a la imagen nueva (`front-stable` → 1.1.0) y recién
después el peso vuelve a 0 y el canary baja a 0 réplicas (lo automatiza `rollout.sh`, Fase 5).
Ese orden importa: si primero bajáramos el canary, el tráfico volvería a la 1.0.0 por un rato.

### "El peso no sabe cuántos pods hay"
El peso reparte entre **Services**, no entre pods:
```
peso 50 →  50% → front-canary (1 pod)   = 50% de la carga en 1 pod
           50% → front-stable (2 pods)  = 25% por pod
```
El pod canary trabaja el **doble** que cada stable. Por eso, para el estrés A/B se escala
el canary a 2 réplicas: condiciones comparables.

### Por qué los Deployments son "idénticos"
Mismos requests/limits (50m/64Mi – 250m/128Mi), mismas probes, mismo `imagePullPolicy`.
Si el canary tuviera más CPU y anduviera más rápido, no sabríamos si es por la versión o
por los recursos. Es un **experimento controlado**: una sola variable cambia (la versión).

### Selector inmutable
El selector es `app + track`, **sin `version`**. Un selector no se puede modificar después de
creado; si incluyera la versión, promover la stable a 1.1.0 obligaría a borrar el Deployment
(con corte). Así es un simple cambio de imagen.

### Probes en /version.txt
Liviano, estático y propio de **esa** imagen. Ojo: también da 200 en la v1.2.0 rota:
las probes dicen "el pod sirve archivos", no "la página funciona" (eso lo mide k6/browser).

### Frase para la presentación
> "Stable y canary son dos Deployments idénticos salvo la versión, cada uno con su Service.
> El Ingress Controller decide por header, después por cookie y después por peso; con
> afinidad, cada usuario queda en una sola versión. La API va aparte para no distorsionar el HPA.
> Y peso 100 no es promover: promover es cambiar la imagen de la stable."

### Posibles preguntas (preparar bien estas)
- *¿Quién reparte el tráfico, Kubernetes o nginx?* El Ingress Controller (nginx). Kubernetes
  solo balancea **dentro** de cada Service.
- *¿Por qué no un solo Service con 3 pods (2 viejos + 1 nuevo)?* Daría ~33% fijo, sin control
  del porcentaje, sin forzar por header/cookie y sin afinidad por versión.
- *¿Qué es exactamente el 10%?* Un sorteo sobre requests sin header/cookie/afinidad. Por eso
  medimos el % **observado** con k6 y curl y lo comparamos con el configurado.
- *¿Cómo se hace el rollback?* Peso a 0 (una anotación, efecto en segundos, sin reiniciar pods).
- *¿Qué pasa con un usuario que ya estaba en el canary cuando hago rollback?* Esto hay que
  **verificarlo en la práctica** con el script de conteo (Fase 5): con peso 0, el tráfico nuevo
  va a la stable; la cookie de afinidad vieja vence a los 3600 s como máximo. Si en la demo se
  ve que algún navegador sigue en el canary, se borra la cookie o se baja el canary a 0 réplicas.
- *¿Por qué ingress-nginx si está retirado?* ingress-nginx dejó de mantenerse en marzo de 2026;
  el reemplazo es **Gateway API** (HTTPRoute con `weight` en backendRefs). El concepto de canary
  es el mismo; lo usamos porque es el addon de Minikube que pide la consigna.

---

## Cuándo sacar capturas y filmar (en Ubuntu)

**En pocas palabras:** mientras escribimos el código no hay nada que capturar. La evidencia sale
cuando se **ejecuta** en Ubuntu. Es la prueba de que lo que decimos realmente pasó.
El paso a paso detallado va a estar en `GUIA_EJECUCION.md`.

| Momento | Qué | Formato | Demuestra |
|---|---|---|---|
| **1. Después de `deploy.sh`** | `kubectl get pods,svc,ingress,hpa -n terrasense -L track,version` | captura | Todo levantado; stable y canary conviviendo |
| | Navegador en `terrasense.local` (v1.0.0) | captura | La app funciona |
| **2. Línea base TP3** | Salida de k6 `smoke` y `load` | captura | SLOs del back (<1% errores, p95 <300 ms) |
| | `stress` + `kubectl get hpa -w` al lado | **video** | El HPA escalando de 2 a N pods |
| | E1: k6 corriendo + `kubectl delete pod` | **video** | Recuperación ante la caída de un pod |
| | E2 spike `MODE=oom` + `kubectl get pods -w` | **video** | OOMKilled y reinicio |
| **3. Canary etapa 0** (peso 0 + cookie) | Navegador normal (1.0.0) y otro con cookie `canary=always` (verde) | captura | Se prueba el canary sin exponer usuarios |
| **4. Rollout 10 → 25 → 50 → 100** | `rollout.sh` corriendo | **video** | Avanza solo si los thresholds dan OK |
| | `conteo-curl.sh` en cada peso | captura | % observado vs % configurado |
| | `bitacora.csv` al final | captura | Registro de decisiones |
| **5. Demo rollback con v1.2.0** | Navegador en blanco + `rollout.sh` volviendo a peso 0 | **video (el más importante)** | El proceso frena un release roto |
| | Consola del navegador (F12) con el `TypeError` | captura | La causa de la pantalla en blanco |
| **6. Estrés A/B** | Resumen k6 de stable y de canary | captura | La hipótesis (p95 ±10%, 200 cargas/s) |
| **7. CI (Fase 6)** | GitHub Actions en rojo y después en verde | captura | La quality gate funciona |

**Se generan solos:** `browser-canary.js` guarda screenshots en `evidencias/capturas/`, y
`front-canary-split.js`, `front-stress.js` y `rollout.sh` escriben JSON/CSV en `evidencias/reportes/`.

**Reglas para que valgan como evidencia:**
- Que se vea `date` en la terminal (o un `watch` con la hora) en cada captura y video.
- Video con pantalla partida: terminal + navegador o `kubectl -w`.
- Nombre descriptivo, ej. `evidencias/videos/05-rollback-v1.2.0.mp4`.
- Grabar en Ubuntu: SimpleScreenRecorder o el atajo `Ctrl+Alt+Shift+R` de GNOME.

---

## Fase 4 — Scripts k6 del canary y del estrés

### En pocas palabras
La Fase 3 dejó el Ingress repartiendo tráfico entre stable y canary. Esta fase agrega las
**mediciones** que deciden si el canary avanza o vuelve a 0: qué versión recibió cada visita,
cuánto tardó, si hubo errores, si hubo assets mezclados y si la pantalla quedó en blanco.

Son 4 archivos. Cada uno responde **una pregunta**:

| Script | Pregunta que responde |
|---|---|
| `front-common.js` | (no es una prueba) Función compartida: carga una página completa (HTML + assets) y verifica versiones |
| `front-canary-split.js` | ¿El Ingress reparte según el peso configurado? ¿El canary tiene latencia y errores aceptables? |
| `browser-canary.js` | ¿El usuario **ve** la página o ve una pantalla en blanco? (Chromium real, ejecuta el JS) |
| `front-stress.js` | ¿Hasta qué carga (cargas de página/s) cada versión cumple el SLO? |

### Conceptos nuevos
- **Threshold**: una regla "pasa / no pasa" escrita **antes** de correr la prueba
  (ej. "menos de 1% de errores"). Si no se cumple, k6 termina con error (código 99) y
  `rollout.sh` lo usa para decidir si avanza o hace rollback. Es el SLO convertido en código.
- **p95**: el 95% de las visitas tardó menos que este valor. Se usa en vez del promedio porque
  el promedio esconde a los usuarios que esperaron mucho.
- **Counter / Trend / Rate** (tipos de métrica de k6):
  Counter = cuenta (visitas). Trend = guarda tiempos y calcula p95. Rate = porcentaje de "sí" (errores).
- **handleSummary**: función que k6 corre al final; acá la usamos para guardar un **JSON de evidencia**
  en `evidencias/reportes/` y para mostrar un resumen corto en español.
- **Tag**: etiqueta que se le pone a un request (ej. `escalon: 200`) para filtrar métricas después.

### 1) `front-common.js` — cómo carga una página un visitante
```
visitante nuevo (sin cookies)
   │ GET /            → lee X-App-Version del HTML (ej. 1.1.0)
   │ busca en el HTML los /assets/ (CSS, JS)
   │ GET /assets/...  → (en paralelo, como el navegador)
   ▼
asset SANO = status 200  Y  misma versión que el HTML
asset ROTO = 404, o vino de la otra versión (assets mezclados)
```
- Cada vuelta **borra las cookies**: así cada visita es un usuario nuevo y el Ingress la
  sortea de nuevo por peso. Si no, un usuario virtual de k6 se quedaría pegado a la primera versión
  que le tocó y el % medido sería falso.
- Mide dos tiempos: **solo HTML** (lo que mide un chequeo HTTP simple) y **página** (HTML + el
  asset más lento; más parecido a lo que espera el usuario).

### 2) `front-canary-split.js` — el reparto y la salud de cada versión
- Llegan **20 visitas por segundo durante 5 minutos** (`RATE`, `DURATION`), **sin** cookie ni
  header: tráfico equivalente al de usuarios reales, que el Ingress reparte por peso.
- Anota por separado canary y stable: visitas, tiempos (HTML y página) y errores. También los assets rotos.
- **Thresholds (criterios para avanzar de etapa):**
  | Regla | Por qué |
  |---|---|
  | `http_req_failed < 1%` | El sistema en general no falla |
  | `err_canary < 1%` | La versión nueva no falla |
  | `lat_canary p95 < 300 ms` | La versión nueva es rápida (mismo SLO que el back) |
  | `assets_rotos < 1%` | La afinidad funciona: nadie recibe una página mezclada |
- Guarda `evidencias/reportes/<ETAPA>-split.json` con **% canary observado vs peso configurado**
  (ej. peso 10 → observado 9,8%). El sorteo es aleatorio: es normal que no dé exacto.

### 3) `browser-canary.js` — lo que ve el usuario
- **Chromium de verdad**: ejecuta el JavaScript, que es lo que k6 HTTP no hace.
- 20 visitas (`N`), cada una en un **contexto nuevo** (= un usuario distinto, sin cookies).
- Espera 2,5 s (para que el JS dibuje), lee el `<meta app-version>` y mira si
  `body.innerText` está vacío → **pantalla en blanco**.
- Threshold `pantalla_blanca rate == 0`: **tolerancia cero**. Una sola pantalla en blanco ya es un incidente.
- Saca una captura de cada visita: `evidencias/capturas/<ETAPA>-visita-07-v1.1.0.png`
  (o `...-v1.2.0-BLANCA.png`). **Evidencia automática.**
- `FORZAR_CANARY=1` pone la cookie `canary=always` → prueba el canary con **peso 0** (etapa 0).

### 4) `front-stress.js` — estrés A/B (Actividad 2)
- **A/B**: la misma prueba contra cada versión **por separado**, para comparar.
  `TARGET=stable` manda `X-Canary: never`; `TARGET=canary` manda `X-Canary: always`.
- Carga en escalones (cargas de página por segundo):
```
 800 |                                              ┌──────┐
 400 |                                   ┌──────┐  ╱       │
 200 |                       ┌──────┐   ╱        ╲╱        │  ← la hipótesis se evalúa ACÁ
 100 |            ┌───┐     ╱        ╲_╱                    │
  50 |  ┌───┐    ╱     ╲___╱                                │
     └──┴───┴───┴───────────────────────────────────────────┴── tiempo (≈ 9 min)
      10s de subida antes de cada meseta; 1 min las dos primeras, 2 min el resto
```
- Cada request lleva el tag `escalon` (50, 100, 200...) según el tiempo transcurrido; los
  10 s de subida se etiquetan "subida" para no mezclarlos con la meseta.
- **Thresholds sobre el escalón 200** (el de la hipótesis): errores < 1%, p95 < 300 ms.
  Además, `version_inesperada == 0`: si apareciera la otra versión, el header no funcionó y
  la medición no serviría.
- Guarda `evidencias/reportes/estres-front-<TARGET>.json` con el **p95 por escalón**, los
  errores, los **bytes por página** y las **iteraciones descartadas**.

### Cómo leer los resultados
1. Mirá primero **`thresholds: OK / FALLARON`**: es la respuesta corta.
2. En el split: **% observado ≈ peso** (±3 puntos está bien con unos miles de visitas).
   Si el canary tuviera 0 visitas con peso 25, el Ingress canary no se aplicó.
3. **p95 canary vs p95 stable**: la regla de la Fase 5 es "canary ≤ stable + 10%, o la diferencia < 5 ms".
   La tolerancia de 5 ms existe porque en Minikube los tiempos son de pocos ms: un 10% de 4 ms es
   ruido, no una diferencia real. Además, la v1.1.0 pide 2 assets que la v1.0.0 no pide (tiene el CSS
   adentro), así que su "página" siempre suma un poco más.
4. En el estrés: buscá **en qué escalón el p95 se dispara o aparecen errores** (punto de quiebre)
   y comparalo entre stable y canary.
5. **Iteraciones descartadas** altas = la PC que genera la carga no dio abasto: ese escalón no es
   confiable (el límite lo puso k6, no la app).

### Por qué un canary necesita los dos tipos de prueba
```
k6 HTTP (split/estrés)   → miles de visitas, mide tiempos y errores    → NO ve la pantalla en blanco
k6 browser               → pocas visitas, ejecuta JS como un usuario   → SÍ ve la pantalla en blanco
```
Uno mide **cantidad** (rendimiento, fiabilidad) y el otro **lo que ve la persona** (calidad en uso).
Con la v1.2.0, el split da todo OK (200 en todo) y el browser da `pantalla_blanca` = 100% → rollback.

### Frase para la presentación
> "Escribimos los criterios de aceptación antes de correr, como thresholds de k6. El split mide
> si el reparto es el configurado y si el canary es igual de rápido y sin errores; el navegador
> real detecta la pantalla en blanco que el HTTP no ve; y el estrés A/B compara las dos versiones
> en igualdad de condiciones para contrastar la hipótesis."

### Posibles preguntas
- *¿Por qué constant-arrival-rate y no N usuarios fijos?* Con usuarios fijos, si el sistema se pone
  lento, cada usuario manda menos requests y la carga **baja sola**: se esconde el problema.
  Con llegada constante, la carga se mantiene como en la realidad.
- *¿Por qué el browser hace solo 20 visitas?* Un navegador real consume mucha CPU y memoria. Para
  detectar una pantalla en blanco alcanza con pocas visitas: si la versión está rota, falla siempre.
- *¿Por qué el estrés usa header y no peso?* Con peso, cada versión recibe una parte distinta de la
  carga. Con el header, cada corrida le pone **toda** la carga a una sola versión: comparación justa.
- *¿Por qué escalar el canary a 2 réplicas para el estrés?* Para que tenga los mismos pods que la stable;
  si no, compararíamos 1 pod contra 2.

---

## Fase 5 — Scripts de despliegue y rollout

### En pocas palabras
Las fases 1 a 4 dejaron escritos los manifiestos y las pruebas. Esta fase agrega los scripts
que **ejecutan** todo en orden: levantar el cluster, cambiar el peso del canary, contar el
reparto y correr el plan de rollout completo, decidiendo en cada etapa si se avanza o se hace
rollback. Que esté automatizado hace que el plan sea **reproducible** (se ejecuta igual cada vez)
y que la decisión dependa de criterios escritos, no de quien lo mira.

| Script | Qué hace |
|---|---|
| `deploy.sh` | Levanta todo desde cero en Minikube |
| `peso.sh <N>` | Cambia el % de tráfico al canary y lo registra con la hora |
| `conteo-curl.sh [N]` | Cuenta qué versión responde, con curl y con los logs del Ingress |
| `rollout.sh` | Ejecuta el plan de rollout completo con decisiones automáticas |

Se corren desde `tp-final/`: `./scripts/deploy.sh`.

### `deploy.sh` — despliegue en un Minikube limpio
```
minikube start (driver docker)
   └► addons: ingress (ingress-nginx) + metrics-server (CPU para el HPA)
       └► build de 4 imágenes DENTRO de Minikube (docker-env)
           terrasense-back:1.0.0, terrasense-front:1.0.0 / 1.1.0 / 1.2.0
           └► esperar al Ingress controller
               └► base (namespace, config, DB) → back + HPA → stable + canary
                   └► Ingress (con reintentos) → /etc/hosts con la IP de Minikube
```
- **docker-env**: hace que `docker build` construya dentro del Docker de Minikube. Así el
  cluster ya tiene las imágenes sin subirlas a un registry (por eso `imagePullPolicy: IfNotPresent`).
- **Orden**: la DB primero, porque el back no pasa la readiness sin DB.
- **Reintentos en el Ingress**: ingress-nginx tiene un *webhook de validación* (un servicio que
  revisa cada Ingress antes de aceptarlo). Tarda unos segundos más que el pod en estar disponible;
  si se aplica antes, rechaza el Ingress. Por eso se reintenta 12 veces cada 5 s.
- **/etc/hosts**: asocia `terrasense.local` y `api.terrasense.local` a la IP de Minikube.

### `peso.sh <N>` — cambiar el peso
1. `kubectl annotate ... canary-weight=N`: el Ingress controller recarga en segundos, **sin reiniciar pods**.
2. Actualiza el YAML con `sed`: el repo queda igual que el cluster (si alguien vuelve a
   aplicar el YAML, no pisa el peso con un valor viejo).
3. Escribe en `evidencias/reportes/cambios-de-peso.log`: `2026-11-18T10:05:00-03:00 peso 10 -> 25`.
   Con esa hora se cruza cada cambio con las métricas y los videos.

### `conteo-curl.sh [N]` — verificación independiente de k6
- N curls (default 100) a `/version.txt` sin cookies → `sort | uniq -c`:
  ```
       74 1.0.0
       26 1.1.0      ← con peso 25, ≈ 25%
  ```
- Además cuenta en los **logs del Ingress controller** cuántos requests fueron a `front-canary`.
- Son dos fuentes distintas (cliente y servidor) que deben coincidir con el peso. Si k6 dice
  25% y curl también, el dato es confiable.

### `rollout.sh` — el plan de rollout automatizado
```
                    ┌─────────────────────────────────────┐
                    │ preparar canary con VERSION_CANARY  │ (siempre con peso 0)
                    └──────────────────┬──────────────────┘
                                       ▼
          ETAPA 0: peso 0 + navegador con cookie canary=always (3 visitas)
                    ¿0 pantallas en blanco y 3/3 visitas en el canary?
                       │ no                                │ sí
                       ▼                                   ▼
            FALLA (peso ya es 0:               para cada peso en 10 → 25 → 50 → 100:
            ningún usuario expuesto)             peso.sh P
                                                 en paralelo: split (k6 HTTP, 5 min)
                                                              + navegador (20 visitas)
                                                         │
                                ¿thresholds del split OK?
                                ¿0 pantallas en blanco?
                                ¿canary recibió visitas?
                                ¿p95 canary ≤ p95 stable +10%  o  diferencia < 5 ms?
                                    │ alguna no                   │ todas sí
                                    ▼                             ▼
                   ROLLBACK: peso 0, medir cuánto        AVANZA → siguiente peso
                   tardó, anotar en bitácora, cortar             │
                                                                 ▼
                                                   fin del plan (peso 100)
                                                   PROMOVER=1 → promoción
```
**Cada etapa** queda en `evidencias/reportes/bitacora.csv`:
`inicio, fin, etapa, versión, peso, % observado, visitas, p95 canary, p95 stable, errores canary,
assets rotos, pantallas blancas, decisión (AVANZA/ROLLBACK/PROMOCION), motivo`.

Detalles que hay que saber explicar:
- **Etapa 0** prueba la versión nueva con un navegador real **sin exponer usuarios** (peso 0 +
  cookie). Con la v1.2.0, el rollout se frena acá: ningún usuario real ve la pantalla en blanco.
- **Split y navegador en paralelo**: el split mide miles de visitas (reparto, latencia, errores);
  el navegador verifica lo que se ve. Se necesitan los dos (ver Fase 4).
- **Criterio de latencia**: se compara el p95 de **página** del canary contra el de la stable
  **medido en la misma etapa** (misma carga, mismo momento). La tolerancia de 5 ms evita hacer
  rollback por ruido: en Minikube los tiempos son de pocos ms.
- **Peso 100**: no hay visitas a la stable, así que se compara contra el p95 stable de la etapa anterior.
- **Tiempo de rollback**: desde el `peso 0` hasta que 20 requests seguidos ya no reciben la
  versión canary. Es una métrica de **recuperabilidad**.
- **Promoción (PROMOVER=1)**, en este orden:
  1. la stable pasa a la imagen nueva (sed en el YAML + `kubectl apply` + `rollout status`);
  2. peso 0 → todo el tráfico a la stable, que ya es la versión nueva;
  3. canary a 0 réplicas.

  Si se invierte el orden, durante unos segundos el tráfico vuelve a la versión vieja.
- **Sin `set -e`**: k6 termina con código 99 cuando fallan los thresholds. Ese caso no es un error
  del script, es una decisión (rollback), así que se maneja a mano.

Variantes de uso:
| Comando | Para qué |
|---|---|
| `./scripts/rollout.sh` | Plan completo con la 1.1.0 (≈ 20 min) |
| `DURATION=1m ./scripts/rollout.sh` | Ensayo rápido |
| `SOLO_PROMOVER=1 ./scripts/rollout.sh` | Promover una versión ya validada |
| `VERSION_CANARY=1.2.0 ./scripts/rollout.sh` | Demo: la etapa 0 frena la versión rota |
| `VERSION_CANARY=1.2.0 SALTEAR_ETAPA0=1 PESOS="25" ./scripts/rollout.sh` | Demo: rollback con tráfico real y tiempo de rollback medido |

### Frase para la presentación
> "El plan de rollout está automatizado en rollout.sh: en cada peso corre k6 HTTP y un navegador
> real en paralelo, y solo avanza si se cumplen criterios escritos antes. Si algo falla, vuelve a
> peso 0, mide cuánto tardó y lo deja en la bitácora. Con la v1.2.0, el proceso la frena en la
> etapa 0, antes de que la vea un usuario."

### Posibles preguntas
- *¿Por qué automatizar y no cambiar el peso a mano?* Para que la decisión dependa de criterios
  fijados de antemano y quede registrada; a mano es fácil "dejar pasar" un resultado dudoso.
- *¿Cuánto tarda un rollback?* Lo mide el script (queda en la bitácora). Es un cambio de anotación:
  el Ingress controller recarga en segundos y no se reinicia ningún pod.
- *¿Por qué la etapa 0 usa solo 3 visitas?* Es una verificación de humo de la UI: si la versión está
  rota, falla siempre; no hace falta volumen.
- *¿Por qué hay dos demos con la 1.2.0?* La primera muestra el caso ideal (se frena sin exponer a
  nadie). La segunda muestra qué pasa si igual llega a usuarios reales: el navegador la detecta
  en el 25% y el rollback la saca en segundos.
- *¿Qué pasa si se corta la luz a mitad del rollout?* El peso queda en el último valor aplicado
  (está en el cluster y en el YAML). Se vuelve a correr desde la etapa que corresponda con `PESOS`.
