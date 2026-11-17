# RESUMEN — TP Final (apunte para la defensa)

Apunte de estudio, fase por fase: qué se hizo, para qué sirve, cómo se conecta
con lo anterior y cómo explicarlo en la presentación.

**Cómo leer este apunte:** primero leé "El TP en 2 minutos" (el mapa). Después cada
fase arranca con **En criollo** (la idea sin tecnicismos) y recién ahí viene el detalle.

---

## ★ El TP en 2 minutos (leer esto primero)

### La historia
TerraSense es una empresa con sensores en el campo que mandan temperatura y humedad a
un servidor (**back**). Los dueños miran esos datos en una página web (**front**).

Una madrugada de helada subieron una versión nueva del front que dejaba **la pantalla en
blanco**. El monitoreo decía "todo OK" (el servidor respondía), pero nadie podía ver los
datos justo cuando más importaban.

**La pregunta del TP:** ¿cómo sacamos una versión nueva sin que pueda volver a pasar eso?

### La respuesta: "probar con pocos antes de dárselo a todos"
Analogía: un restaurante que cambia una receta. No la cambia para todos de golpe: se la sirve
primero a **1 de cada 10 mesas**, mira si les gusta, y recién después a 1 de cada 4, a la
mitad, a todos. Si a esas primeras mesas les cae mal, vuelve a la receta vieja y casi nadie se
enteró. Eso es un **canary**.

```
 Versión vieja (1.0.0) ─┐
                        ├─► "portero" (Ingress) decide quién ve cuál ─► usuarios
 Versión nueva (1.1.0) ─┘     10% → 25% → 50% → 100%   (si algo falla → 0%)
```

### Las piezas, en una línea cada una
| Pieza | En criollo | Fase |
|---|---|---|
| Back + base de datos en Kubernetes | El servidor, que se reinicia solo si se cae y suma copias si hay mucha carga | 1 (era el TP3) |
| k6 de carga | "Simulador de sensores": mide cuánto aguanta el servidor antes de cambiar nada (línea base) | 1 |
| Tres versiones del front | 1.0.0 = la actual; 1.1.0 = la nueva (verde, para que se note); 1.2.0 = **rota a propósito** | 2 |
| Stable + canary + Ingress | Las dos versiones corriendo juntas y el "portero" que reparte usuarios | 3 |
| k6 del canary y de estrés | "Clientes de prueba": miden si la nueva anda igual o mejor que la vieja | 4 |
| Scripts (rollout.sh) | El "piloto automático": sube el % solo si las mediciones dan bien; si no, vuelve a 0 | 5 |
| CI (GitHub Actions) | El "control de calidad en la puerta": revisa el código (linters, Horusec) antes de construir nada | 6 |
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
de a poco; si están mal, se vuelve a 0% (**rollback**) y casi nadie se enteró.
(El nombre viene del canario que los mineros llevaban: si el canario se moría, había gas
y se salía antes de que le pasara algo a la gente.)

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

**En criollo:** mientras escribimos el código no hay nada que capturar. La evidencia sale
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
