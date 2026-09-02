> **Documento de metodología (archivado).** Registro de una investigación o decisión tomada durante el desarrollo. La validación de datos se hizo en un espacio de trabajo aparte (`data-experiment/`, no incluido en este repositorio); las rutas a `reports/`, `raw_data/` y `scripts/*.py` se refieren a ese espacio, no a este repo. Índice de docs: [`docs/README.md`](./README.md).

---

# Investigación previa a la Fase 7 — endpoints de partido de Sportmonks

Mismo criterio que la Fase 0: comprobar contra la API real, con muestra
pequeña, antes de diseñar el esquema. **No hay esquema ni ETL todavía.**

- Fecha: 2026-08-30. Temporada: LaLiga 2024/25 (`league_id=564`,
  `season_id=23621`).
- Script: `scripts/08_investigate_fixtures.py`.
- Respuestas crudas: `raw_data/sportmonks/fixtures_investigation/`
  (`01_schedule_full.json`, `bulk_page1.json` = 50 fixtures con todos los
  includes, `fixture_<id>.json` ×4 con detalle por jugador).
- Muestra de 4 partidos: 19135254 (J1 Villarreal-Atlético), 19135375
  (J13 Mallorca-Atlético), 19135503 (J26 Rayo-Sevilla), 19135669
  (J38 Girona-Atlético).

---

## 1. Calendario — `/schedules/seasons/{season_id}`

- **1 petición devuelve los 380 partidos** de la temporada (38 jornadas ×
  10), anidados en `stage 'Regular Season' -> rounds[] -> fixtures[]`.
- Cada fixture trae ya, sin includes extra: `id`, `name`
  ("Villarreal vs Atlético de Madrid"), `starting_at`, `result_info`
  ("Game ended in draw." / "Atlético Madrid won after full-time."),
  `state_id`, `round_id`, y **auto-incluye `participants` y `scores`**.
- 380/380 con `result_info` (temporada cerrada).
- Entidad de rate-limit: **`Stage`** (bucket distinto de `Fixture`).

## 2. Formaciones — `include=formations`

- **Se dan como string limpio** (`"4-2-3-1"`, `"4-4-2"`, `"3-4-2-1"`…).
  NO hay que inferirlas de las posiciones. 2 filas por fixture (una por
  equipo), clave `participant_id` + `location`.
- **50/50 fixtures de la muestra tienen las dos formaciones.** Sin huecos.
- Es **por partido**, no por equipo-temporada: el mismo equipo aparece con
  formaciones distintas según la jornada (Atlético: 3-4-2-1, 4-4-1-1,
  4-4-2 en 3 partidos distintos). Bien para el cruce formación→resultado.
- Distribución en la muestra (100 apariciones): 4-2-3-1 ×37, 4-4-2 ×21,
  4-3-3 ×15, 4-1-4-1 ×8, 5-3-2 ×6, 3-4-3 ×5, 4-5-1 ×4, 3-4-2-1 ×3.

## 3. Alineaciones — `include=lineups` (`lineups.details.type` para stats por jugador)

- Filas por jugador, **clave `team_id`** (ojo: NO `participant_id`; pero
  `team_id == participants[].id`, ver §5).
- `type_id = 11` → titular (siempre 11 por equipo); `type_id = 12` →
  suplente/banquillo (7-11, varía).
- **Titulares traen `formation_field`** = rejilla `"fila:columna"`
  (`"1:1"` portero, `"2:3"` central, `"4:2"` medio…) y `formation_position`
  = slot 1-11. Reconstruye la forma exacta sobre el campo.
- `position_id`: 24=POR, 25=DEF, 26=MED, 27=DEL (grupo grueso).
- Suplentes: `formation_field = null`.
- Cada jugador trae `details[]` = **sus stats de ESE partido** (mismos
  codes que las stats de temporada de Fase 0: `accurate-passes`,
  `aeriels-won`, `big-chances-created`, `clearances`, `duels-won`…). No
  hace falta para el Team Style, pero está disponible (infla el JSON: la
  página de 50 fixtures con `lineups.details.type` pesa 25 MB; sin ese
  include, mucho menos).
- Consistente en los 4 partidos: siempre 11 titulares con rejilla + banco.

## 4. Estadísticas de equipo — `include=statistics.type`

- Filas `{participant_id, location, type: {code}, data: {value}}`.
- **Siempre para AMBOS equipos** (50/50 fixtures, 2 participantes con
  stats). No pasa lo de API-Football de traer solo uno.
- **Mismo patrón "Sportmonks omite el 0" de la Fase 0:** el conjunto de
  `codes` varía por partido (31 a 41 tipos). Reparto en la muestra de 50:

  **Presentes en los 50 fixtures (23 codes) — el núcleo fiable:**
  `ball-possession`, `passes`, `successful-passes`,
  `successful-passes-percentage`, `long-passes`, `shots-total`,
  `shots-on-target`, `shots-off-target`, `shots-blocked`,
  `shots-insidebox`, `shots-outsidebox`, `corners`, `fouls`, `tackles`,
  `interceptions`, `total-crosses`, `accurate-crosses`,
  `successful-dribbles`, `successful-dribbles-percentage`,
  `dribble-attempts`, `saves`, `throwins`, `goals-kicks`.

  **Intermitentes (≈zero-omission):** `attacks` 49/50, `dangerous-attacks`
  49, `offsides` 49, `key-passes` 49, `yellowcards` 49, `goal-attempts`
  49, `free-kicks` 48, `successful-long-passes(-percentage)` 48,
  `big-chances-created` 45, `big-chances-missed` 43, **`goals` 43**,
  `hit-woodwork` 26, `penalties` 13, `redcards` 11.

  **Muy escasos (no fiables):** `duels-won` 9/50, `assists` 9,
  `successful-headers` 9, `counter-attacks` 2, `challenges` 2.

- **NO hay xG** a nivel de partido. El include `xgfixture` da **403**
  ("You do not have access") y `expected-goals` no aparece en ningún
  fixture. Igual que en la Fase 4 con las stats de temporada: el Team
  Style Profile hay que construirlo sin xG.
- **`statistics.goals` NO es fiable** (43/50, se omite cuando un equipo
  marca 0). Para el marcador usar `scores` (ver §5).

## 5. Cruce equipo → formación → resultado → stats — **limpio**

Todo cuelga del **mismo `participant_id`** (formations, statistics,
scores), y **`participants[].id == lineups.team_id`** (verificado:
Athletic 13258, Getafe 106 en ambos sitios). El único "salto" es que
lineups etiqueta por `team_id` en vez de `participant_id`, pero es el
mismo número.

- **Marcador final:** `scores[]` con `description == "CURRENT"` (una fila
  por equipo, `score.goals` + `score.participant` = home/away). Presente
  en 50/50. También hay `1ST_HALF`, `2ND_HALF`, `2ND_HALF_ONLY`.
- `state.state == "FT"` confirma partido terminado.
- Los 4 partidos de prueba cruzaron sin ningún obstáculo:
  equipo → formación (string) → marcador (scores) → 23+ stats de equipo.

**Sin obstáculos reales para el cruce.** IDs consistentes, sin datos que
falten en el núcleo.

## 6. Coste de la temporada completa

| Vía | Peticiones | Notas |
|---|---|---|
| **Bulk paginado** (recomendada) | **8** | `/fixtures?filters=fixtureSeasons:23621&include=participants;formations;statistics.type;lineups&per_page=50` → 380/50 = 8 páginas. Trae calendario + formaciones + stats de equipo + alineaciones de golpe. |
| 1 petición/fixture | 380 (+1 calendario) | `/fixtures/{id}?include=…`. Innecesario. |
| `/fixtures/multi/{ids}` | ~8-19 | Acepta includes; lotes de ~20-50 ids. |

- `per_page` máx **50** cuando hay includes (sin includes se queda en 25 a
  menos que se use `filters=populate`).
- **Límite observado: 2000 peticiones / hora / entidad.** Cualquiera de
  las vías entra de sobra en una sola ventana; no hace falta trocear.
- Si se añade `lineups.details.type` (stats por jugador y partido) el
  volumen de datos sube mucho (~25 MB/página) pero el nº de peticiones no
  cambia. Para el Team Style Profile probablemente no haga falta ese
  include.

## Resumen para el diseño de la Fase 7

- **Formación**: string por partido y equipo, fiable, sin huecos. Permite
  tanto "formación dominante del equipo" como "formación por partido".
- **Stats de equipo por partido**: 23 codes fiables (posesión, pases,
  tiros por zona, córners, faltas, entradas, intercepciones, centros,
  regates…), siempre para ambos equipos. Sin xG. `goals` va por `scores`.
- **Cruce formación↔resultado↔stats**: sin fricción, todo por
  `participant_id` (= `team_id`).
- **Coste**: 8 peticiones para la temporada entera. No hay problema de
  cuota.
- **Pendiente de decidir juntos (Fase 7):** unidad del perfil (equipo-
  temporada agregado vs por-partido), qué stats entran y cómo se
  normalizan (¿per-90? ¿% ya vienen dados?), si el perfil incluye la
  distribución de formaciones o solo la modal, y si se guardan las stats
  del rival (para "estilo defensivo" = lo que concede).
