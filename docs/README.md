# docs/

Registro de decisiones, metodología y notas de desarrollo del proyecto.
La mayoría son documentos **archivados** de fases de validación e
investigación que se hicieron en un espacio de trabajo aparte
(`data-experiment/`, no incluido en este repositorio) — se conservan aquí
porque el *cómo se decidió* es parte del proyecto.

| Documento | Qué es |
|---|---|
| [`DECISIONS.md`](DECISIONS.md) | Registro de decisiones de arquitectura, fechado y con justificación (fuente de datos, convenciones de esquema, licencia). Una decisión no se revierte sin otra entrada que lo diga. |
| [`roles_fase4_mapping.md`](roles_fase4_mapping.md) | Fase 4: mapa rol → campos → ¿construible? Por qué 4 roles y no 7, contrastado contra la completitud real del dato por posición. |
| [`fase7_fixtures_investigation.md`](fase7_fixtures_investigation.md) | Investigación previa al Team Style Profile: qué devuelve Sportmonks para partidos (formaciones, estadísticas de equipo, xG). |
| [`fase11_coach_investigation.md`](fase11_coach_investigation.md) | Por qué el entrenador por temporada **no** se persiste: las fechas de tenencia de Sportmonks son incoherentes en los límites. |
| [`fase12_migration_investigation.md`](fase12_migration_investigation.md) | Validación de datos antes de añadir la temporada 2025/26 y Segunda División: sin regresión de calidad, coste de la carga, diseño multi-competición. |
| [`TOS_ARCHIVE.md`](TOS_ARCHIVE.md) | Transcripción y análisis de los términos de uso de datos de Sportmonks y API-Football (due diligence, no asesoramiento legal). |
| [`session_notes.md`](session_notes.md) | Diario de desarrollo: un bloque por tarea, con lo que se hizo, las decisiones y la validación de sanidad. Largo y de tono interno. |
