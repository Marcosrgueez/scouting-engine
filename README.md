# scouting-engine

Motor de scouting de fútbol. Código de producción del proyecto (el
experimento de validación de datos vive aparte, en `../data-experiment/`).

**Fase actual: 12a — multi-temporada.** LaLiga **2024/25 y 2025/26**
conviven en las mismas tablas (diferenciadas por `season_id`); la API y el
frontend tienen selector de temporada (por defecto, la más reciente).
Segunda División queda para la Fase 12b (pendiente de reconfigurar el plan
de Sportmonks — ver `../data-experiment/docs/fase12_migration_investigation.md`).
(Fases previas: 1 esquema, 2 ETL, 3 percentiles, 5 Player Role Score,
6 Similarity Engine, 7 Team Style Profile, 8 Tactical Fit Score, 9 API,
10 Frontend, 11 resúmenes narrativos.)

## Requisitos

- Python 3.10+
- PostgreSQL 14+ local. Instalado en esta máquina con
  `winget install PostgreSQL.PostgreSQL.17` (servicio `postgresql-x64-17`,
  puerto 5432, superusuario `postgres`).

## Puesta en marcha

```powershell
cd scouting-engine
python -m venv venv ; .\venv\Scripts\Activate.ps1
pip install -r requirements.txt

Copy-Item .env.example .env
# Editar .env si la contraseña de postgres no es "postgres".

# Crear la base de datos una vez:
& "C:\Program Files\PostgreSQL\17\bin\createdb.exe" -U postgres scouting

# Crear el esquema + poblar catálogos estáticos (positions, stat_types):
python -m db.create_schema
# (para empezar de cero: python -m db.create_schema --drop)

# Smoke test (Fase 1): cargar solo los 13 jugadores de prueba:
python -m loaders.smoke_test_load

# ETL masivo (Fase 2): cargar el roster completo de LaLiga 24/25.
python -m loaders.etl_laliga --dry-run --limit 14   # prueba rapida
python -m loaders.etl_laliga                        # carga real (idempotente)
# LaLiga 25/26 (Fase 12a): mismo pipeline, otra temporada. Convive con 24/25.
#   1. descargar el crudo: cd ../data-experiment && python -m scripts.10_fetch_season --season-id 25659
python -m loaders.etl_laliga --season-dir s25659    # DELETE scoped por season_id, no toca 24/25

# ETL de partidos (Fase 7): team_fixtures + team_fixture_statistics.
python -m loaders.etl_team_fixtures                                   # 24/25 (si es la unica temporada)
python -m loaders.etl_team_fixtures --sportmonks-season-id 25659 --season-dir s25659   # 25/26
python -m loaders.etl_team_fixtures --sportmonks-season-id 23621 --offline             # 24/25 explicito

# Analisis (Fases 3/5/6/8). Todos toman --season-id (id interno de la BD)
# para recalcular una sola temporada; sin el, procesan todas las cargadas
# (el PARTITION separa por season+competition, no se contaminan).
python -m analysis.percentiles                      # umbral 900 min
python -m analysis.percentiles --season-id 3        # solo 25/26 (DELETE scoped)
python -m analysis.percentiles --min-minutes 750    # el umbral es un parametro

# Player Role Score (Fase 5): score de encaje 0-100 por rol, con desglose.
python -m analysis.role_scores --dry-run            # calcula y hace rollback
python -m analysis.role_scores                      # usa percentiles de umbral 900
python -m analysis.role_scores --min-minutes 750    # si recalculaste percentiles a 750

# Player Similarity (Fase 6): top-20 similar por jugador (cosine, mismo bucket).
python -m analysis.similarity --dry-run             # calcula y hace rollback
python -m analysis.similarity                       # usa percentiles de umbral 900
python -m analysis.similarity --explain "Pedri"     # top-20 ya calculado de un jugador

# Ejes de estilo de equipo (Fase 8, parte precalculada): percentiles por eje.
python -m analysis.team_style --dry-run
python -m analysis.team_style                       # umbral 5 partidos/formacion (Fase 7)

# Tactical Fit Score (Fase 8): se calcula BAJO DEMANDA, no hay tabla.
python -m analysis.tactical_fit --player "Pedri" --role deep_lying_playmaker --explain
python -m analysis.tactical_fit --team "FC Barcelona" --role ball_winner --top 10
python -m analysis.tactical_fit --player "Isco" --team "Osasuna" --by-formation --explain
python -m analysis.tactical_fit --player "Rodri" --w-role 0.6 --w-style 0.4   # peso ajustable

# API (Fase 9 + 12a): expone todo por HTTP. ?season= en cada endpoint
# (id, sportmonks_season_id o nombre '2025/2026'); por defecto la mas reciente.
python -m uvicorn api.main:app --reload        # -> http://127.0.0.1:8000/docs
#   GET /seasons               -> temporadas cargadas (para el selector del frontend)
#   GET /players?season=2024/2025   -> jugadores de esa temporada

# Frontend (Fase 10): React + Vite. Necesita la API corriendo.
cd frontend && npm install && npm run dev      # -> http://localhost:5173
```

## Estructura

```
db/
  database.py        engine + Session (lee DATABASE_URL del .env)
  models.py          los 20 modelos SQLAlchemy
  seed_catalogs.py   datos estáticos de positions y stat_types
  create_schema.py   create_all() + seed (sin Alembic todavía)
loaders/
  schemas.py            modelos Pydantic del JSON de Sportmonks (validacion + mapper)
  sportmonks_mapping.py  helpers JSON -> esquema interno (compartidos)
  smoke_test_load.py     Fase 1: carga puntual de 13 jugadores
  etl_laliga.py          Fase 2: ETL masivo del roster, idempotente
  etl_team_fixtures.py   Fase 7: ETL de partidos (formaciones + stats de equipo), idempotente
api/
  main.py              Fase 9: FastAPI app, CORS, routers. Sin auth. Swagger en /docs
  dependencies.py        sesion de DB por request
  routers/               players, teams, roles, scouting
  services/              llaman a analysis/ o consultan las tablas ya pobladas
  schemas/               Pydantic de request/response (NO confundir con loaders/schemas.py)
frontend/              Fase 10: React + Vite. 4 pantallas sobre la API. Ver frontend/README.md
analysis/
  percentiles.py         Fase 3: per-90 + percentiles por bucket, idempotente
  role_scores.py         Fase 5: Player Role Score con pesos, idempotente
  similarity.py          Fase 6: Player Similarity Engine (cosine, top-20), idempotente
  team_style.py          Fase 8: ejes de estilo por equipo/formacion (percentiles), idempotente
  tactical_fit.py        Fase 8: Tactical Fit Score, funcion parametrizada BAJO DEMANDA
  narrative.py           Fase 11: resumenes por reglas (jugador y estilo de equipo), sin LLM
```

## Percentiles (`analysis/percentiles.py`)

Puebla `player_percentiles` de forma idempotente (DELETE scoped + INSERT).

- **Umbral de minutos** = parametro de `recompute()` (`--min-minutes`, por
  defecto **900** = 10 partidos). NO es constante ni columna de config. Un
  jugador por debajo simplemente no tiene filas en `player_percentiles`.
- **Normalizacion** (`stat_types.normalization`):
  - `per90` — todos los contadores: `(suma / minutos) * 90`.
  - `raw` — `accurate-passes-percentage` (ya es %) y `rating` (media 0-10);
    entre etapas se hace media ponderada por minutos.
  - `none` — `minutes-played` (es el propio umbral) y `appearances`
    (disponibilidad, no rendimiento) NO entran.
- **Percentil** = `PERCENT_RANK` dentro de
  `(season, competition, position_bucket, stat_type)`, orientado con
  `stat_types.direction` -> **100 = mejor de su bucket, siempre**
  (para `lower_better` como tarjetas o perdidas se invierte).
- Los ceros imputados (`is_imputed_zero`) cuentan como el 0 que son.
- `goals-conceded` / `cleansheets` / `saves` son `goalkeeper_only`: solo se
  calculan dentro del bucket `portero`.

**Caveats conocidos** (no son bugs, son limites del dato de temporada):
- Las stats de volumen defensivo por-90 (tackles, intercepciones...)
  infravaloran a los centrales de equipos dominadores (p.ej. Rüdiger sale
  bajo porque el Madrid tiene el balon y el rival casi no llega). Un
  ajuste por posesion es mejora futura.
- `saves` per-90 de un portero depende de los tiros recibidos, no solo de
  su nivel; sin "tiros a puerta recibidos" no se puede sacar % de paradas.
  `goals-conceded` y `cleansheets` sí son informativos.

## ETL (`loaders/etl_laliga.py`)

Reutiliza el JSON ya descargado en `../data-experiment/raw_data/sportmonks/`
(no vuelve a pedir a la API salvo `--fetch-missing` para huecos puntuales).

```
player_stats/{id}.json
  -> validacion Pydantic (loaders/schemas.py)   [si falla: log + skip]
  -> upsert players            (ON CONFLICT sportmonks_player_id)
  -> upsert player_team_season (ON CONFLICT player_id+season_id+order_in_season)
  -> upsert player_statistics  (ON CONFLICT player_team_season_id+stat_type_id)
```

**Idempotente:** relanzarlo no duplica nada. Cada jugador se procesa
"borrar sus etapas (cascade a sus stats) + reinsertar", con commits por
lotes de 50, así que si se corta a la fila 400 se puede relanzar sin
limpiar la BD.

## Player Role Score (`analysis/role_scores.py`)

Puebla `player_role_scores` + `player_role_score_breakdown` de forma
idempotente (DELETE scoped + INSERT), a partir de `player_percentiles`
(Fase 3) y del catálogo `roles` / `role_buckets` / `role_weights`.

- **4 roles "construibles plenos"** (`../data-experiment/docs/roles_fase4_mapping.md`):
  `ball_winner`, `deep_lying_playmaker`, `advanced_playmaker`,
  `ball_playing_cb`. Un jugador solo recibe score en un rol si el `bucket`
  de su `primary_position` está en `role_buckets`.
- **Pesos por nivel** (`role_weights.tier`, informativo): núcleo 3,
  apoyo 1.5, contexto 0.5. El cálculo usa solo `role_weights.weight`.
- **Fórmula:** `score = SUM(percentil × peso) / SUM(peso)`, ya en `[0,100]`.
- **Métricas faltantes → se excluyen del numerador y del denominador**
  (el peso se renormaliza sobre lo disponible), NO se imputan a percentil
  50. Motivo: los percentiles de Fase 3 ya imputan los ceros omitidos de
  Sportmonks antes de rankear, así que un percentil bajo ya significa
  "hace poco de esto"; un percentil ausente significa falta de dato (otra
  liga/temporada), e imputar 50 inventaría una media que no tenemos.
  `player_role_scores.total_weight` (< peso del rol ⇒ había huecos) y
  `metrics_used` son provenance. Guarda: si el peso disponible cae por
  debajo del **60 %** del peso del rol, no se emite fila.
  En LaLiga 2024/25 la cobertura es del 100 % → 0 jugadores afectados.
- **Explicabilidad:** `player_role_score_breakdown` guarda una fila por
  métrica con `percentile`, `weight` y `contribution` (= percentil × peso).
  `SUM(contribution) / SUM(weight)` sobre esas filas reproduce el `score`.

## Player Similarity Engine (`analysis/similarity.py`)

Puebla `player_similarity` de forma idempotente (**DELETE scoped +
INSERT**). Para cada jugador, guarda solo su **top-20 más similar** dentro
de su mismo `bucket` y temporada — NO la matriz N² completa.

- **Vector de features:** los percentiles per90 de `player_percentiles`
  (Fase 3), **todas las métricas del bucket** (34 de campo; 37 portero,
  con las 3 solo-portero). La cobertura de Fase 3 es del 100 % dentro de
  cada bucket → todos los vectores están alineados y completos.
- **Distancia:** cosine similarity sobre el percentil crudo `[0,100]`
  (todo positivo → similitud en `[0,1]`). Los scores se agrupan alto
  (top-1 típico 0.88-0.94); **lo que discrimina es el ranking**, no el
  valor absoluto. Verificado a ojo: lateral ofensivo y lateral defensivo
  puro NO salen en el top-20 el uno del otro.
- **Solo mismo bucket.** Sin comparación cross-posición en esta fase.
- **Idempotencia = DELETE scoped + INSERT** (no upsert): el top-20 de un
  jugador puede cambiar de miembros entre pasadas y un upsert dejaría
  filas viejas colgando.
- La tabla **no es simétrica** (que B esté en el top-20 de A no implica lo
  contrario, ni con el mismo score/rank).

**Filtros de edad y lado = parámetros de consulta, NO del cálculo.** Se
aplican con un `WHERE` al leer `player_similarity` (join a `players`
`birth_date` / `positions.lado`); la similitud estadística entre dos
jugadores no cambia según el filtro que se use después. Ejemplo — similares
a X sub-23 y por la izquierda:

```sql
SELECT sp.name, ps.similarity_score, ps.rank
FROM player_similarity ps
JOIN players p  ON p.id = ps.player_id
JOIN players sp ON sp.id = ps.similar_player_id
JOIN positions pos ON pos.id = sp.primary_position_id
WHERE p.name = 'Lamine Yamal'
  AND date_part('year', age(DATE '2025-05-25', sp.birth_date)) < 23
  AND pos.lado = 'izquierda'
ORDER BY ps.rank;
```

**Fuera de alcance (pendientes conocidos):** pie dominante
(`players.preferred_foot` sigue NULL en todo el roster) y valor de mercado
(sin fuente en ningún proveedor). Ningún filtro puede apoyarse en ellos
todavía.

## Team Style Profile (`loaders/etl_team_fixtures.py`)

Perfil de equipo construido desde **datos reales de partido**, no a mano.
Grano **crudo por partido**: 1 fila por (equipo, partido) en
`team_fixtures` + sus stats en `team_fixture_statistics`. **La agregación
por formación (V/E/D, medias, por venue) se hace por consulta (`GROUP BY`),
no en la carga** — mismo principio que `player_team_season` /
`player_statistics`.

- **Descarga:** bulk paginado de Sportmonks
  (`/fixtures?filters=fixtureSeasons:{id}&include=participants;formations;statistics.type;scores;state&per_page=50`),
  **8 peticiones** para los 380 partidos. JSON crudo en
  `../data-experiment/raw_data/sportmonks/fixtures/page_NN.json`. `lineups`
  NO se descarga (el perfil no lo usa; inflaba el JSON ~20×).
- **Catálogo `team_stat_types`** (15 codes: posesión, pases + precisión +
  largos, tiros total/puerta/dentro/fuera, córners, faltas, tackles,
  intercepciones, centros totales + precisos, regates). **Separado de
  `stat_types`** (stats de jugador) a propósito: varios `code` coinciden
  pero la entidad y la unidad son distintas (total de un equipo en un
  partido vs per-90 de temporada de un jugador), y `normalization` /
  `direction` / `valid_for` de `stat_types` no aplican a una stat de
  equipo.
- **`goals` NUNCA sale de statistics** (Sportmonks lo omite en 0):
  `goals_for` / `goals_against` vienen siempre de `scores[]`
  (`description == "CURRENT"`); `result` se deriva.
- **Ceros omitidos:** `is_imputed_zero` como en `player_statistics` —
  se imputa 0 en stats `count` ausentes, las `percentage` (posesión,
  precisión) no se imputan. En LaLiga 24/25: solo 4 filas imputadas de
  22 800.
- **`is_conceded`:** `false` = stat propia; `true` = la misma stat del
  rival en ese partido (perfil defensivo, gratis del mismo fixture). No
  duplica filas de `team_fixtures`.
- **Idempotente:** DELETE scoped por `season_id` (+ cascade) + INSERT. No
  upsert (el set de stats presentes de un partido puede cambiar entre
  descargas).

Umbral sugerido al agregar: **≥5 partidos por formación** (`HAVING
count(*) >= 5`) — por debajo, la V/E/D y las medias son ruido de
calendario. Filtro de consulta, no almacenado.

## Tactical Fit Score (`analysis/tactical_fit.py`)

Compatibilidad jugador-equipo:

```
tactical_fit = w_role · role_score  +  w_style · style_compatibility
```

Ambos componentes en `[0,100]`, `w_role + w_style = 1` → score en `[0,100]`.
Pesos **70/30 por defecto, como parámetro** (`--w-role` / `--w-style`), no
hardcodeado. Heurística explícita — sin datos de evento no hay forma de
*aprender* qué perfil rinde en qué estilo.

- **No se materializa.** El producto cartesiano jugador×equipo×rol×formación
  (~34 k filas de `0.7·a + 0.3·b`) quedaría obsoleto al tocar el peso. Se
  calcula **bajo demanda** con una función parametrizada (decisión
  consultada, patrón "función parametrizada" como los percentiles de
  Fase 3). Lo que sí se precalcula (parte cara y reutilizable): los
  percentiles de estilo en **`team_style_axes`** (325 filas).
- **5 ejes de estilo** (percentil del equipo entre los 20 de LaLiga, para
  el equipo+formación o el agregado si la formación no llega a 5 partidos):
  `possession`, `pass_accuracy`, `crossing_frequency` (centros/partido),
  `press_intensity` (tackles+intercepciones/partido), `directness`
  (long-passes/passes).
- **Matriz rol→estilo** (`role_style_weights`, catálogo, **pesos planos
  1.0** — la matriz de diseño solo da signos y hay 1-3 ejes por rol, los
  tiers de Fase 5 añadirían precisión falsa):

  | rol | ejes |
  |---|---|
  | Deep-Lying Playmaker | +possession, +pass_accuracy, **−directness** |
  | Ball Playing CB | +possession, +pass_accuracy |
  | Advanced Playmaker | +crossing_frequency |
  | Ball Winner | +press_intensity |

  `direction = negative` → en el cálculo se usa `100 − percentil` (directitud
  alta perjudica a un Deep-Lying Playmaker).
- **`style_compatibility` = `SUM(pctl_efectivo · peso) / SUM(peso)`** — misma
  forma de combinar que el Role Score de la Fase 5. El desglose por eje
  (`--explain`) dice qué eje sumó y qué eje restó.
- **Caveats:** `press_intensity` (tackles+intercepciones) no es presión
  real (necesita datos de evento / PPDA); mide "actividad defensiva", que
  correlaciona con MENOS posesión — hereda el caveat de posesión de
  Fase 3. Advanced Playmaker y Ball Winner tienen un solo eje de estilo,
  así que su `style_compatibility` es ese único percentil.

## API (`api/`)

FastAPI que expone las Fases 1-8. **Sin autenticación.** Swagger en
`/docs`, ReDoc en `/redoc`, esquema en `/openapi.json`. CORS abierto (`*`)
porque el frontend (Fase 10) es un cliente aparte sin cookies.

```powershell
pip install -r requirements.txt          # añade fastapi + uvicorn
python -m uvicorn api.main:app --reload   # http://127.0.0.1:8000/docs
```

**La API no reimplementa nada de `analysis/`.** `routers/` → `services/` →
(módulos de `analysis/` o consultas a las tablas que esos módulos ya
poblaron). El Tactical Fit se calcula **en vivo por request** (función de
Fase 8), no se cachea.

**Fase 12a — `?season=`:** casi todos los endpoints aceptan `season`
(id interno, `sportmonks_season_id` o nombre `'2025/2026'`); sin él, la
temporada más reciente cargada. Cada consulta filtra por `season_id` — las
dos temporadas nunca se mezclan. La edad se calcula a fin de la temporada
consultada (no "hoy"). `/roles` es catálogo, no lleva `season`.

| Método | Ruta | Qué hace |
|---|---|---|
| GET | `/seasons` | Temporadas cargadas + cuál es la default (para el selector del frontend). |
| GET | `/players` | Lista paginada (`offset`/`limit`/`total_count`). Filtros: `bucket`, `team_id`, `min_minutes` (900), `age_min`, `age_max`, `side`, `season`. |
| GET | `/players/{id}` | Bio + `photo_url` + equipo + bucket/lado + percentiles + **`summary`** (frase por reglas: mejor rol + sus métricas core, Fase 11). 404 si no existe; `percentiles: []` si < umbral. |
| GET | `/players/{id}/similar` | Top-20 de `player_similarity` ya calculado. Filtros `age_max`/`side` **sobre el resultado** (rank conserva su número). |
| GET | `/players/{id}/roles` | Role scores del jugador + desglose completo de `player_role_score_breakdown`. |
| GET | `/players/{id}/best-teams` | **Tactical Fit invertido (Fase 11):** ranking de los 20 equipos por encaje del jugador. `?role_id` opcional (si no, el de mayor score). Cada equipo con su `team_narrative`. |
| GET | `/teams` | Los 20 equipos. |
| GET | `/teams/{id}/style` | Estilo por formación desde `team_style_axes` + **`narrative`** (descripción por reglas, Fase 11). Formaciones con < 5 partidos en `formations_below_threshold` (nombre + nº, sin ejes) — ver decisión abajo. |
| GET | `/roles` | Los 4 roles con `metric_weights` (Fase 5) y `style_weights` (Fase 8). |
| POST | `/scouting/tactical-fit` | Body `{team_id, role_id, formation?}`. Ranking de jugadores por `score` desc con desglose + **`team_narrative`**. Formación sin muestra → 422 con la lista de formaciones disponibles. |

**Fase 11 — resúmenes narrativos por reglas** (`analysis/narrative.py`,
sin LLM: plantillas fijas, deterministas, auditables). `player_role_summary`
(mejor rol + 2-3 métricas core de mayor contribución; si no hay rol, lo
dice explícitamente) y `team_style_narrative` (los 1-2 ejes de estilo más
alejados del percentil 50, con umbrales ≥70 / ≤30). **Sin entrenador:** la
investigación de la Fase 11
(`../data-experiment/docs/fase11_coach_investigation.md`) concluyó que las
fechas de tenencia de Sportmonks no son fiables para fijar el entrenador de
una temporada pasada; la narrativa usa solo el nombre del equipo.

**Errores:** 404 (id inexistente), 422 (Pydantic para body/query inválido;
también para `formation`/`team_id` sin datos suficientes, con mensaje que
explica qué falta y qué alternativas hay).

**Decisión — formaciones bajo el umbral de 5 en `/teams/{id}/style`:** se
**incluyen, marcadas como muestra insuficiente**, en un array aparte
`formations_below_threshold` con solo `formation` + `n_matches` y **sin
ejes de estilo**. Motivo: `team_style_axes` nunca las materializó (Fase 7
filtra en la carga con `HAVING count(*) >= 5`), así que no hay percentiles
que devolver; pero omitirlas del todo le ocultaría al frontend que el
equipo también usó esas formaciones. El dato crudo sale de `team_fixtures`
por `GROUP BY`, que es el patrón de acceso que la Fase 7 diseñó.

## Esquema

Catálogos: `competitions`, `seasons`, `teams`, `positions`, `stat_types`,
`roles`, `role_buckets`, `role_weights`, `team_stat_types`,
`role_style_weights`.
Entidades: `players`, `player_team_season`, `player_statistics`,
`team_fixtures`, `team_fixture_statistics`.
Derivado (Fase 3): `player_percentiles`.
Derivado (Fase 5): `player_role_scores`, `player_role_score_breakdown`.
Derivado (Fase 6): `player_similarity`.
Derivado (Fase 8): `team_style_axes` (el Tactical Fit en sí no se
almacena — función bajo demanda).

Puntos de diseño que vienen del experimento de Fase 0
(`../data-experiment/docs/DECISIONS.md`):

- **Fuente única de estadísticas: Sportmonks.** `stat_types.source_provider`
  por defecto `sportmonks`. `players.apifootball_player_id` se guarda solo
  como referencia cruzada.
- **Multi-etapa:** `player_team_season` permite varias filas por
  (jugador, temporada) — cesiones / traspasos dentro de la liga.
  Se numeran con `order_in_season` (0, 1, ...) y el unique constraint va
  sobre `(player_id, season_id, order_in_season)`. Se descartó usar
  `date_from` (Sportmonks no da fechas de etapa fiables; `NULL != NULL` en
  el índice no desduplicaría). Las stats cuelgan de cada etapa; la
  agregación se hace con `SUM ... GROUP BY`.
- **Ceros omitidos:** Sportmonks no devuelve una estadística cuando vale 0.
  Al cargar se imputa `value = 0, is_imputed_zero = true` para que el
  cálculo de percentiles (Fase 3) no sobrestime a los jugadores flojos.
  Los campos base (minutos, apariciones, pases, precisión, rating,
  duelos ganados) NO se imputan: si faltan, el jugador no jugó.
- **Stats solo-portero:** `stat_types.valid_for = 'goalkeeper_only'` para
  `saves`, `goals-conceded` y `cleansheets`. El loader solo crea esas filas
  para jugadores con `bucket = 'portero'`. (`goals-conceded` / `cleansheets`
  en Sportmonks vienen también para jugadores de campo pero son stats de
  equipo; `saves` siempre es 0 para jugadores de campo.)
