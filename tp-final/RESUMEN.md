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
