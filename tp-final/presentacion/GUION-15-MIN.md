# Cómo explico este TP en 15 minutos

**Idea central (decirla al principio y al final):** un "200 OK" no significa que el usuario ve la
página. Por eso el release pasa por dos quality gates: el CI controla el **código** y el canary
controla la **aplicación corriendo**, con criterios escritos antes de medir.

| Min | Tema | Qué decir | Qué mostrar |
|---|---|---|---|
| 0–1 | **Problema** | TerraSense: sensores en el campo y un panel web. En la helada, un release dejó la pantalla en blanco con el monitoreo en verde. Pregunta: ¿cómo liberar sin repetirlo? | Diagrama de arquitectura (README §0) |
| 1–3 | **Línea base (TP3)** | Back en Kubernetes: probes (readiness saca el pod del Service, liveness lo reinicia) y HPA por CPU (el % se calcula sobre el request). k6 mide antes de cambiar nada: 67 req/s nominal, stress hasta el quiebre, pod eliminado, OOM | Captura del load en verde; video del HPA escalando o del OOMKilled |
| 3–5 | **CI = gate 1** | Reutiliza TP1 (linters) y TP2 (Horusec). La imagen solo se construye si pasan las dos gates. Pasó de verdad: 22 hallazgos → rojo → 14 corregidos, 5 falsos positivos, 3 riesgos aceptados → verde | Captura del run rojo y del verde; tabla de `HALLAZGOS-HORUSEC.md` |
| 5–6 | **Tres versiones** | Un Dockerfile para las tres. Versión marcada en el header, el meta y version.txt. 1.1.0 = la candidata; 1.2.0 = rota a propósito: 200 en todo, pantalla en blanco | Navegador 1.0.0 vs 1.1.0; Network en 200 + consola con TypeError |
| 6–9 | **Canary = gate 2** | Dos Deployments idénticos salvo la versión, dos Services. El Ingress decide header → cookie → peso. Afinidad para no mezclar assets. API en otro Ingress, sin afinidad, para no distorsionar el HPA. Peso 100 no es promoción | Diagrama del Ingress (RESUMEN Fase 3); captura de etapa 0 con cookie |
| 9–11 | **Rollout automatizado** | Plan escrito antes: etapa 0 con peso 0, después 10/25/50/100. En cada etapa, k6 HTTP + navegador real. Avanza solo si: thresholds OK, 0 pantallas en blanco, p95 ≤ stable +10%. Si no, rollback medido | Video del rollout; bitácora; conteo curl vs peso |
| 11–12 | **Demo v1.2.0** | El split da OK (todo 200); el navegador ve la pantalla en blanco → rollback en X s. En la etapa 0 ni siquiera llega a usuarios | **Video del rollback** (el más importante) |
| 12–13 | **Estrés A/B** | Hipótesis escrita antes: la 1.1.0 no empeora el p95 más de 10% y ambas sostienen 200 cargas/s con <1% de errores. A/B con header, canary a 2 réplicas, peso 0. Resultado: _completar_ | Tabla de escalones de las dos versiones |
| 13–14 | **ISO/IEC 25000** | Cada prueba evidencia una característica de 25010: linters → mantenibilidad; Horusec → seguridad; probes/fallas → fiabilidad (recuperabilidad, 25045); HPA y k6 → eficiencia de desempeño; canary → fiabilidad y adecuación funcional. Los SLOs son requisitos (2503n), k6 mide (2502n), rollout.sh evalúa (2504n). El navegador acerca la calidad **en uso** (25019). Sin cubrir: accesibilidad (Lighthouse/axe), interoperabilidad (contract testing), seguridad en ejecución (ZAP) | Tabla del README §4.1 |
| 14–15 | **Veredicto y aprendizaje** | Go/no-go de la 1.1.0 y de 10.000 sensores (≈ 333 req/s): _completar_. Aprendizajes: assets mezclados → afinidad; peso ≠ pods; peso 100 ≠ promoción; SAST marca comentarios; ingress-nginx retirado → Gateway API | README §6 y §7 |

## Tres frases para memorizar
1. "El CI controla el código; el canary controla el comportamiento con tráfico real; los dos con criterios fijados antes."
2. "La v1.2.0 responde 200 en todo y deja la pantalla en blanco: solo un navegador real la detecta."
3. "Peso 100 no es promoción: promover es cambiar la imagen de la stable y recién después apagar el canary."

## Preguntas probables (respuesta corta)
- **¿Por qué no un rolling update?** No controla qué % ve la versión nueva ni permite medirla al lado de la vieja.
- **¿Quién reparte el tráfico?** El Ingress controller (nginx), no Kubernetes.
- **¿Cuánto tarda un rollback?** _completar_ s: es una anotación, no reinicia pods.
- **¿Por qué A/B con header y no con peso?** Con el peso, cada versión recibe una parte distinta de la carga.
- **¿Falso positivo vs riesgo aceptado?** El primero no es un problema real; el segundo sí lo es, pero se acepta con una justificación y mitigaciones.
- **¿Qué no cubre?** Accesibilidad, contrato front-API, seguridad en ejecución, dependencias, backup de la DB.
