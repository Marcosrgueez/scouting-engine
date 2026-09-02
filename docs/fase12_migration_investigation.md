> **Documento de metodología (archivado).** Registro de una investigación o decisión tomada durante el desarrollo. La validación de datos se hizo en un espacio de trabajo aparte (`data-experiment/`, no incluido en este repositorio); las rutas a `reports/`, `raw_data/` y `scripts/*.py` se refieren a ese espacio, no a este repo. Índice de docs: [`docs/README.md`](./README.md).

---

# Investigación previa a la Fase 12 — temporada 2025/26 + Segunda División

Mismo criterio que Fase 0 y Fase 7: comprobar con datos reales, con muestra
pequeña, antes de comprometerse a nada. **Nada de ETL ni de esquema.**

- Fecha: 2026-09-02. Script: `scripts/09_investigate_2526.py`.
- Crudos: `raw_data/sportmonks/investigate_2526/`.
- Los datos de LaLiga 2024/25 ya cargados NO se tocan; conviven con lo nuevo.

---

## 1. LaLiga 2025/26 — **completa y lista** ✅

| temporada | season_id | finished | is_current | fechas |
|---|---|---|---|---|
| 2024/2025 | 23621 | true | false | 2024-08-15 → 2025-05-25 |
| **2025/2026** | **25659** | **true** | **false** | 2025-08-15 → 2026-05-24 |
| 2026/2027 | 27965 | false | **true** | 2026-08-15 → 2027-05-30 |

- **`season_id` de LaLiga 25/26 = `25659`.**
- La 26/27 ya está en marcha (`is_current`); la **25/26 es la última cerrada**, como se esperaba, y está **`finished: true`**.
- Vía `/schedules/seasons/25659`: **380 fixtures, 380 con `result_info`, 380 en `state_id = 5` (FT)**. Temporada íntegra, sin partidos pendientes.
- Composición: bajan a Segunda **Real Valladolid, Leganés, Las Palmas**; suben **Real Oviedo (id 93), Levante (3457), Elche (1099)**.

### Calidad de dato de la 25/26 = idéntica a la 24/25

Muestra de 15 regulares (≥900 min), completitud de los 21 campos que
sostienen los 4 roles construibles:

- **100 %**: `minutes-played`, `appearances`, `passes`,
  `accurate-passes-percentage`, `rating`, `duels-won`, `clearances`,
  `long-balls`, `long-balls-won`.
- **93 %**: `tackles`, `interceptions`, `aeriels-won`, `fouls` (1 jugador
  con 0 → omitido).
- **60-87 %**: `key-passes`, `successful-dribbles`, `dribble-attempts`,
  `through-balls`, `blocked-shots`, `big-chances-created`, `goals`,
  `assists`.

**Es exactamente el patrón de zero-omission de la Fase 4** ("Sportmonks
omite el detalle con valor 0"): en una muestra mezclada de defensas y
medios, `goals`/`assists`/`big-chances-created` salen bajos porque muchos
de esos jugadores tienen 0. Restringiendo a la posición relevante (Fase 4:
`goals` 96 % delanteros, `blocked-shots` 100 % central/lateral) y con la
imputación de 0 que ya hace el ETL, **los 4 roles siguen siendo
construibles plenos con la misma calidad y los mismos caveats. No hay
regresión.**

### Fixtures 25/26 (Team Style Profile) = idéntico

`/fixtures?filters=fixtureSeasons:25659&include=participants;formations;statistics.type;scores;state&per_page=50`:
50/página, `has_more` (→ 8 páginas para 380). Página 1: **50/50 con las 2
formaciones**, **50/50 con stats de ambos equipos**, **35 codes presentes
en los 50 fixtures** (incluye los 15 `team_stat_types` que usa la Fase 7,
más `attacks`/`goals`/`key-passes`/`duels-won` que en la muestra de 24/25
eran intermitentes → 25/26 va igual o mejor). **Sin xG** (`xgfixture` →
403, igual que siempre).

---

## 2. Segunda División — **NO accesible en el plan actual** ❌

- El plan es **`Starter` (5 ligas), en TRIAL hasta 2026-09-12** (luego
  pasa a Starter de pago).
- `/leagues` devuelve las 5 ligas elegidas: **Premier League (8),
  Bundesliga (82), Ligue 1 (301), Serie A (384), La Liga (564)**. Los 5
  huecos están ocupados por las cinco grandes primeras divisiones.
- `/leagues/567` y `/leagues/566` (candidatos a LaLiga 2) →
  *"…you don't have access to it via your current subscription."*
- `/leagues/search/Segunda` → **0 resultados** (la búsqueda también está
  scopeada a la suscripción).

**No se puede validar la calidad de dato de Segunda porque no hay acceso a
Segunda.** Para incluirla haría falta una de estas tres:

1. **Cambiar una de las 5 ligas** por LaLiga 2 (se pierde esa liga; el
   proyecto solo usa La Liga, así que cambiar p.ej. Ligue 1 → LaLiga 2 es
   viable sin coste, pero es una decisión del usuario y hay que ver si el
   plan Starter permite reconfigurar las ligas sin penalización).
2. **Añadir LaLiga 2 como liga extra** (add-on de pago sobre el Starter).
3. **Subir de plan** (planes con más ligas).

Hasta que eso se resuelva, **la Fase 12 se reduce a cargar LaLiga
2025/26**.

---

## 3. Percentiles por competición — **la recomendación se confirma, y no hay obstáculo técnico**

**Recomendación: percentiles / role scores / team style se calculan
SEPARADOS por `(competition_id, season_id)`.** Nada de lo investigado la
cambia; al contrario, la refuerza:

- Un p90 en Segunda ≠ p90 en LaLiga (nivel distinto) y **no hay League
  Strength Coefficient** para ajustar. Mezclar los pools daría rankings
  sin sentido.
- Aunque Segunda no entre ahora, **el mismo principio aplica entre
  temporadas de LaLiga**: el percentil de un jugador en 25/26 debe ser
  frente a sus pares de 25/26, no frente a un pool 24/25+25/26 mezclado.

### El diseño actual YA lo soporta — sin rediseño

- **`analysis/percentiles.py`**: `PERCENT_RANK() OVER (PARTITION BY
  season_id, competition_id, position_bucket, stat_type)`. Ya rankea
  separado por competición-temporada. `--season-id` / `--competition-id`
  scopean el DELETE+INSERT → recalcular 25/26 no toca 24/25.
- **`analysis/role_scores.py`**, **`analysis/similarity.py`**,
  **`analysis/team_style.py`**, **`analysis/tactical_fit.py`**: todas
  toman `season_id` (y competition donde aplica) como parámetro y scopean
  el DELETE.
- **Constraints de unicidad**: todas incluyen `season_id` en la clave
  (`player_percentiles (player_id, season_id, stat_type_id)`,
  `player_role_scores (player_id, season_id, role_id)`,
  `player_similarity (player_id, similar_player_id, season_id)`,
  `team_style_axes (team_id, season_id, formation, style_axis)`,
  `team_fixtures (sportmonks_fixture_id, team_id)`). **Un jugador/equipo
  puede tener filas de las dos temporadas sin conflicto.**
- **Catálogos** (`players`, `teams`): `sportmonks_*_id` único → un jugador
  que juega las dos temporadas = 1 fila; equipos ascendidos (Oviedo,
  Levante, Elche) = filas nuevas; los descendidos se quedan (los referencia
  la data 24/25).

### El único trabajo real está en la capa de API (no en `analysis/`)

Hoy la API asume **una sola temporada**:
- `api/dependencies.py::get_season_id` → `ORDER BY Season.id LIMIT 1`.
- Los servicios (`players.py`, `teams.py`, `scouting.py`) consultan
  `player_percentiles` / `player_role_scores` / `team_style_axes` **sin
  filtrar por temporada**, y `_MINUTES_SUBQ` **suma minutos de todas las
  etapas del jugador** (sumaría 24/25 + 25/26).

Con 2 temporadas cargadas eso **mezclaría datos**. Fase 12 tiene que:
- resolver "qué temporada" (por defecto la más reciente; opcionalmente
  `?season=` como query param);
- añadir `.where(X.season_id == season)` a ~8 consultas de servicio;
- el frontend: selector de temporada, o simplemente fijar la más reciente.

Es un cambio pequeño y localizado. **`analysis/` y el esquema no se
tocan.**

---

## 4. Coste de la migración

**Solo LaLiga 25/26** (Segunda no accesible). Roster real: **768 entradas
de plantilla** en los 20 equipos (media 38/equipo, incluye traspasos a
mitad de temporada — como las 762 de 24/25).

| paso | endpoint | peticiones | entidad rate-limit |
|---|---|---|---|
| liga + temporadas | `/leagues/564?include=seasons` | 1 | League |
| equipos 25/26 | `/teams/seasons/25659` | 1 | Team |
| plantillas | `/squads/seasons/25659/teams/{id}` × 20 | 20 | Squad |
| stats por jugador | `/players/{id}?include=statistics.details.type&filters=…` × ~768 | ~768 | **Player** |
| mapa de posiciones | `/core/types` (model_type=position) | 1 | Type |
| fixtures (Team Style) | `/fixtures?filters=…&per_page=50` × 8 | 8 | Fixture |
| **total** | | **~799** | |

- **Límite: 2000 peticiones / hora / entidad.** El cuello de botella son
  las ~768 peticiones `Player`, y **768 < 2000/hora → entra en una sola
  ventana horaria con margen** (precedente: la carga de 762 de 24/25 en
  Fase 0 dejó la cuota en ~1250/2000).
- Es una descarga **puntual** (luego el ETL reutiliza el JSON, como en
  Fase 2).
- Si en el futuro entra Segunda (~750 jugadores más), serían ~1500
  peticiones `Player` — sigue bajo 2000/hora, pero convendría trocear en
  2 ventanas por seguridad.

**Aviso no técnico:** la suscripción está en **trial hasta 2026-09-12**;
después se factura como Starter de pago. La reconfiguración de ligas (para
meter Segunda) hay que mirarla en el panel de `my.sportmonks.com`.

---

## Resumen para decidir el diseño de la Fase 12

1. **LaLiga 25/26: lista.** season_id 25659, 380/380 FT, calidad de dato =
   24/25, fixtures = 24/25. Se puede cargar ya.
2. **Segunda: bloqueada** por el plan (5 ligas, todas primeras divisiones).
   Decisión del usuario: cambiar una liga / add-on / upgrade. Sin acceso,
   no se puede validar su calidad.
3. **Percentiles por `(competition_id, season_id)`: confirmado.** El
   esquema y `analysis/` ya lo soportan sin cambios. El trabajo de Fase 12
   es la capa de API (resolver "qué temporada" + filtrar ~8 consultas) y
   el frontend (selector de temporada).
4. **Coste: ~800 peticiones puntuales, entra en una hora.** Trial acaba el
   2026-09-12.

---

## Actualización 2026-09-02 — Segunda División: acceso reconfigurado y validada

El usuario cambió la selección de ligas del plan (sacó **Ligue 1**, metió
**LaLiga 2**). Script: `scripts/11_investigate_segunda.py`. Crudos:
`raw_data/sportmonks/investigate_segunda/`.

### Acceso — CONFIRMADO

`/leagues` ahora devuelve: Premier League (8), Bundesliga (82), Serie A
(384), **La Liga (564)**, **La Liga 2 (567)**. Antes `/leagues/567` daba
"no access"; ahora resuelve.

### league_id / season_id

- **Segunda División (LaLiga 2) = league_id `567`.**
- **2025/26 = season_id `25673`**, `finished: true` (la 26/27 es
  `is_current`).
- **462 fixtures** de Regular Season (22 equipos × 42 jornadas), **462 en
  `state_id = 5` (FT)**, 462 con `result_info`. **Completa.** Los play-offs
  de ascenso aparecen como stages pero con 0 fixtures en `/schedules`
  (no afecta al Team Style, que usa la liga regular).
- `/teams/seasons/25673` devuelve **23 equipos, pero uno es "TBC"** (0
  jugadores, placeholder de Sportmonks). Reales: **22**. Entre ellos, los
  3 descendidos de LaLiga 24/25 (**Real Valladolid, Las Palmas, Leganés**)
  y un filial (**Real Sociedad II**).

### Calidad de dato — comparable a LaLiga, con UNA diferencia real

Muestra de 15 regulares (≥900 min) de Segunda 25/26. Completitud de los 21
campos que sostienen los 4 roles construibles plenos:

- **100 % (o 14/15 = zero-omission puntual):** `minutes-played`,
  `appearances`, `passes`, `accurate-passes-percentage`, `rating`,
  `duels-won`, `tackles`, `interceptions`, `key-passes`, `dribble-attempts`,
  `aeriels-won`, `clearances`, `fouls`, `long-balls`, `long-balls-won`,
  `successful-dribbles` (93 %), `blocked-shots` (93 %).
- **`big-chances-created` 87 %, `assists` 80 %, `goals` 67 %:** el mismo
  patrón de zero-omission de la Fase 4 (muestra mezclada de defensas y
  medios). Verificado con creadores conocidos (Adrián Embarba, extremo,
  3131 min): `big-chances-created` = 16, `key-passes` = 67, `assists` = 12
  — todos presentes.
- **`through-balls` y `through-balls-won`: AUSENTES.** No es 0, no vienen.
  0/15 en la muestra, y ausentes también para Embarba y Fer Niño (jugadores
  ofensivos de alto volumen). En LaLiga 25/26, `through-balls` está en
  36/80 archivos (~62 %, patrón normal de Fase 4). **En Segunda, Sportmonks
  no recoge este campo.**

Diff exacto de codes (muestra Segunda vs 80 archivos de LaLiga): lo único
que aparece en LaLiga y nunca en Segunda son `through-balls`,
`through-balls-won` (y `saves*`, pero es porque la muestra de Segunda no
tenía portero — no es un hueco). Nada aparece en Segunda que no esté en
LaLiga.

**Impacto en los 4 roles — NINGUNO relevante:**
- `through-balls` **nunca fue un campo núcleo** de ningún rol. Fase 4 lo
  clasificó como *"señal secundaria, no núcleo"* al 78 % para Deep-Lying
  Playmaker y Advanced Playmaker (por debajo del umbral del 90 %).
  `through-balls-won` (36 % en LaLiga) nunca fue usable.
- En Fase 5 es un peso de tier **contexto (0.5)** solo para DLP y AP. Al
  cargar Segunda, el pipeline de percentiles lo imputará a 0 para TODOS los
  jugadores de Segunda (misma convención de zero-omission). Efecto: una
  deflación uniforme minúscula del score de DLP/AP en Segunda; **cero
  efecto sobre el ranking dentro de Segunda** (los percentiles son
  scoped por competición-temporada). El guard de cobertura mínima (60 %
  del peso del rol) ni se acerca a activarse: DLP pierde 0.5 de 13.
- **Los 4 roles siguen siendo construibles plenos en Segunda con la misma
  calidad.** Ball Winner y Ball Playing CB no tocan `through-balls`
  siquiera.

### Team Style Profile — idéntico a LaLiga

`/fixtures?filters=fixtureSeasons:25673&include=participants;formations;statistics.type;scores;state&per_page=50`:
50/página (→ ~10 páginas para 462). Página 1: **50/50 con las 2
formaciones**, **50/50 con stats de ambos equipos**, **35 codes en los 50
fixtures**. Los **15 `team_stat_types`** que usa la Fase 7 están **todos al
50/50**. **Sin xG** (`xgfixture` → 403). Funciona igual.

### Coste actualizado

Roster real de Segunda: ~22 equipos × ~35 = **~770 entradas de plantilla**
(Almería 36, Andorra 32...).

| paso | peticiones | entidad |
|---|---|---|
| liga + temporadas | 1 | League |
| equipos | 1 | Team |
| plantillas (×22, se salta "TBC") | 22 | Squad |
| **stats por jugador (~750)** | **~750** | **Player** |
| fixtures (Team Style, ×10 bulk) | 10 | Fixture |
| **total** | **~785** | |

- **Límite: 2000 peticiones / hora / entidad.** Las ~750 `Player` **entran
  en una sola ventana con margen — NO hace falta trocear.** (LaLiga 25/26,
  ya cargada en Fase 12a, fue ~800 y funcionó sin problema.) La estimación
  de "~1500, trocear en 2 ventanas" del punto original asumía cargar LaLiga
  25/26 + Segunda a la vez; como LaLiga 25/26 ya está, Segunda va sola.
- Descarga puntual (el ETL luego reutiliza el JSON).

### Para el diseño de la Fase 12b — a tener en cuenta

- **Dedup de equipos entre ligas.** Valladolid aparece en Segunda 25/26
  con `sportmonks_team_id = 361`; en la carga de LaLiga (Fase 2/12a) su
  `sportmonks_team_id` puede ser otro. Hay que comprobar si Sportmonks usa
  el mismo id de equipo entre competiciones o no, y decidir el `upsert`
  de `teams` en consecuencia (por `sportmonks_team_id`, como ahora, debería
  bastar si el id es estable).
- **Filiales / "TBC".** Real Sociedad II y el placeholder "TBC" (0
  jugadores) — el ETL debe saltarse los equipos sin plantilla.
- **`competition_id`.** Segunda necesita su fila en `competitions`
  (`sportmonks_league_id = 567`). El ETL ya crea competition + season desde
  el `context.json` — `scripts/10 --season-id 25673 --league-id 567`
  produciría el context correcto.
- Todo lo demás (percentiles/roles/similarity/team-style scoped por
  `season_id`, API multi-temporada, frontend con selector) ya está de la
  Fase 12a. El selector del frontend mostrará 3+ opciones; conviene
  agrupar por competición o etiquetar "LaLiga 25/26" / "Segunda 25/26".
