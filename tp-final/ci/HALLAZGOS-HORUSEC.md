# Hallazgos de Horusec — primer run del CI

**Run:** GitHub Actions #43995990963 (commit `e00a083`, 2026-11-17).
**Resultado:** job `horusec` en **rojo** → job `build` **skipped**: la quality gate bloqueó la
construcción de imágenes, que es el comportamiento esperado.

**22 hallazgos** con severidad MEDIUM o mayor (los LOW se ignoran con `-s LOW`).

## Resumen de decisiones

| # | Hallazgo | Herramienta / regla | Severidad | Archivos | Cant. | Decisión |
|---|---|---|---|---|---|---|
| 1 | `Math.random()`: generador de números aleatorios débil | HorusecEngine `HS-JAVASCRIPT-6` | HIGH | `app/back/server.js` (`/api/debug/burn`) | 1 | **Corregido** |
| 2 | Ídem | `HS-JAVASCRIPT-6` | HIGH | `k6/common.js` (4), `k6/spike.js` (1) | 5 | **Falso positivo** |
| 3 | Contenedor puede escalar privilegios | Trivy (misconfig K8s) | MEDIUM | back, front-stable, front-canary, db | 4 | **Corregido** (los 4) |
| 4 | Contenedor corre como root | Trivy | MEDIUM | back, front-stable, front-canary | 3 | **Corregido** |
| 5 | UID bajo (≤ 10000) | Trivy | MEDIUM | back, front-stable, front-canary | 3 | **Corregido** |
| 6 | GID bajo (≤ 10000) | Trivy | MEDIUM | back, front-stable, front-canary | 3 | **Corregido** |
| 7 | Root / UID bajo / GID bajo | Trivy | MEDIUM | `k8s/base/02-db.yaml` (PostgreSQL) | 3 | **Riesgo aceptado** |

Total: **14 corregidos** (1 + 4 + 3 + 3 + 3), **5 falsos positivos** y **3 riesgos aceptados** = 22.

## Justificaciones

### 1. `Math.random()` en `server.js` — corregido
Se usaba en `/api/debug/burn`, el endpoint de laboratorio que consume CPU para probar el HPA.
Ahí no hace falta azar: se reemplazó por un cálculo determinístico (`x = Math.sqrt(x + 1)`).
Fue más simple eliminar la causa que justificarla.

### 2. `Math.random()` en scripts k6 — falso positivo
`HS-JAVASCRIPT-6` advierte que `Math.random()` no sirve para **criptografía**: tokens, claves,
IDs de sesión. En `k6/common.js` y `k6/spike.js` se usa para generar **datos de prueba** (ID de
sensor, temperatura, humedad) y para mezclar tipos de request. Además, estos scripts son
herramientas de prueba de carga: **no se despliegan** ni forman parte de la aplicación. Un valor
predecible no tiene ningún impacto de seguridad. Se registran por hash en
`tp-final/horusec-config.json` (`horusecCliFalsePositiveHashes`).

### 3 a 6. Contenedores del back y del front — corregido
Las imágenes ya corrían como usuarios sin privilegios (`node` UID 1000; nginx UID 101), pero
**los manifiestos no lo exigían**. Trivy lee el manifiesto, no la imagen, y si alguien cambiaba la
imagen por una que corre como root, Kubernetes la habría aceptado. Se agregó a cada contenedor:

```yaml
securityContext:
  runAsNonRoot: true            # K8s se niega a arrancar un contenedor root
  runAsUser: 10001              # back (front: 10101); > 10000 para no chocar con usuarios del nodo
  runAsGroup: 10001
  allowPrivilegeEscalation: false
  capabilities:
    drop: ["ALL"]
```

En el front, nginx necesita escribir en `/var/cache/nginx` y `/tmp` (archivo pid). Con un UID
distinto al de la imagen no tiene permiso, así que se montan dos volúmenes `emptyDir`.
El job `build` del CI verifica que las imágenes **arrancan** con esos mismos UID (ver el workflow).

### 7. PostgreSQL como root — riesgo aceptado (corregido parcialmente)
- **Corregido:** `allowPrivilegeEscalation: false` (hallazgo #3 en `02-db.yaml`).
- **Aceptado:** root, UID bajo y GID bajo.
- **Por qué:** la imagen oficial `postgres` arranca como root para preparar los permisos del volumen
  de datos y después baja al usuario `postgres` (`su-exec`). Forzar un UID no-root desde el inicio
  exige preparar los permisos del volumen a mano (initContainer o `fsGroup`). En Minikube, el
  provisionador de volúmenes `hostPath` no aplica `fsGroup`, y el cambio no se puede validar sin
  arriesgar el despliegue.
- **Mitigaciones vigentes:** la DB no se expone fuera del cluster (Service ClusterIP, sin Ingress);
  la contraseña es aleatoria y no está en el repo (la genera `deploy.sh`); el proceso que atiende
  conexiones corre como `postgres`, no como root; se bloquea la escalada de privilegios.
- **Propuesta para producción:** usar un operador de PostgreSQL (ej. CloudNativePG, que corre sin
  root) o un servicio administrado.
- Registrados por hash en `horusecCliRiskAcceptHashes`.

## Segundo run (#44003617085, commit `6e0af9f`)

Después de las correcciones, quedaron **21 de 22 resueltos**. Quedó **1 hallazgo nuevo**:
`HS-JAVASCRIPT-6` en `server.js`, en un **comentario** que explicaba el cambio y nombraba la
función de random. La regla de Horusec es una expresión regular sobre el texto y no distingue
código de comentarios. Se reescribió el comentario sin nombrar la función.

Esto muestra una limitación del SAST por patrones: puede marcar texto que no se ejecuta.
Siempre hace falta que una persona revise cada hallazgo.

## Limitación detectada: no hay análisis de dependencias (SCA)

El log del run avisa: `Error while running tool NpmAudit: file package-lock.json was not found`.
Sin `package-lock.json`, Horusec **no revisa vulnerabilidades conocidas de las dependencias**
del back (express, pg, cors). El pipeline actual cubre el código propio y la configuración de
K8s, pero **no las librerías de terceros**. Propuesta: versionar `package-lock.json` y usar
`npm ci` en el Dockerfile, para que el build sea reproducible y NpmAudit pueda analizarlo.

## Diferencia entre falso positivo y riesgo aceptado
- **Falso positivo:** la herramienta se equivoca; no hay vulnerabilidad en este contexto.
- **Riesgo aceptado:** el problema **existe**, pero se decide convivir con él por una razón
  documentada, con mitigaciones, y queda pendiente para más adelante.

Los dos quedan **registrados y visibles**: no se borran del análisis, se marcan con su hash.
Si el código cambia, el hash cambia y el hallazgo vuelve a aparecer para revisarlo de nuevo.
