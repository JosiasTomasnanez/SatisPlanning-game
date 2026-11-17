# ci/ — Workflows de los TPs anteriores

Copias **sin modificar** de los workflows de GitHub Actions de los TP1 y TP2, para
tener a mano de dónde sale el pipeline del TP Final. En `main` estos workflows se
borraron (commit `51c78a0`, "se borran actions usados en TP anterior").

| Archivo | Origen | TP | Qué hace |
|---|---|---|---|
| `linter.yml` | rama `feature/configurar-linter`, `.github/workflows/linter.yml` (commit `1438058`) | TP1 | Ruff + Pylint sobre el código Python del juego, en cada PR a `main` |
| `horusec.yml` | rama `dev`, `.github/workflows/horusec.yml` (commit `2ee8437`) | TP2 | Compila Horusec desde el fuente (Go 1.19) y hace SAST, subiendo el reporte como artifact |

Estas copias **no se ejecutan** (GitHub solo ejecuta lo que está en `.github/workflows/`).

## Qué se reutiliza en el TP Final

El workflow activo es `.github/workflows/tp-final-ci.yml` (en la raíz del repo):

| Idea del TP anterior | Cómo aparece en el TP Final |
|---|---|
| Linter como quality gate (TP1) | Job `lint`: htmlhint (front), ESLint (back), hadolint (Dockerfiles). Ruff y Pylint no aplican: TerraSense no tiene Python |
| Horusec compilado desde el fuente (TP2) | Job `horusec`: mismo método, sobre `tp-final/`, ignorando LOW y con `-e true` para que un hallazgo corte el pipeline |
| Reporte como artifact (TP2) | `horusec-report-tp-final` |
| (nuevo) | Job `build` con `needs: [lint, horusec]`: las imágenes candidatas solo se construyen si pasaron las dos gates |
