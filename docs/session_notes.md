# Notas de sesión — scouting-engine

Registro de los resúmenes de fin de tarea, un bloque `## fecha — título`
por tarea. Se añade al final.

## Contexto del proyecto (para lectores sin el repo delante)

**scouting-engine** es el código de producción de un sistema de scouting de
fútbol: dado un rol táctico (p. ej. "central que juega", "mediocentro
destructor"), devolver un ranking de jugadores que encajan, a partir de
percentiles de estadísticas de temporada normalizadas por 90 minutos.

Antes de esto hubo un experimento de validación de datos en
`../data-experiment/` (Fase 0), ya cerrado, que decidió:
- **Sportmonks es la fuente única de estadísticas de jugador.** API-Football
  queda solo como referencia cruzada.
- Sportmonks **omite las estadísticas que valen 0** → hay que imputar 0 al
  cargar, o el cálculo de percentiles sobrestima a los jugadores flojos.
- `goals-conceded` y `cleansheets` en Sportmonks vienen también para
  jugadores de campo, pero son stats de equipo → válidas solo para porteros.
- Un jugador puede tener **varias etapas en una temporada** (cesión /
  traspaso dentro de la liga); las stats vienen separadas por equipo y hay
  que poder agregarlas.

Fases del roadmap: **1 = esquema PostgreSQL (esto)**, 2 = ETL del roster
completo, 3 = percentiles, 4 = taxonomía de roles (cerrada en Fase 0),
5+ = roles de banda, scoring, deploy.

Documentos de decisión heredados: `../data-experiment/docs/DECISIONS.md` y
`../data-experiment/docs/roles_fase4_mapping.md`.

---

## 2026-08-30 — Fase 1: esquema PostgreSQL + smoke test

**Entorno.** PostgreSQL no estaba instalado. Elegido (por el usuario)
instalar local con winget: `PostgreSQL.PostgreSQL.17` (17.11), servicio
`postgresql-x64-17`, puerto 5432, superusuario `postgres` / contraseña
`postgres`. Base de datos `scouting` creada. Nota: el instalador de winget
se quedó pillado en una ventana pidiendo la contraseña del superusuario (el
manifiesto no la pasa); acabó completándose. `.env` del proyecto apunta a
`postgresql+psycopg2://postgres:postgres@localhost:5432/scouting`.

**Proyecto nuevo `scouting-engine/`** (fuera de `data-experiment/`):
`db/` (models.py, database.py, seed_catalogs.py, create_schema.py),
`loaders/smoke_test_load.py`, `.env.example`, `requirements.txt`, `README.md`.
Sin Alembic todavía (el esquema se crea con `python -m db.create_schema`).
**Aún no es un repo git** — pendiente de decidir con el usuario.

**Esquema (8 tablas, SQLAlchemy 2.0):** catálogos `competitions`,
`seasons`, `teams`, `positions`, `stat_types`; entidades `players`,
`player_team_season`, `player_statistics`. Índices en
`player_statistics(stat_type_id)`, `player_statistics(player_team_season_id)`,
`player_team_season(player_id)`, `player_team_season(season_id, competition_id)`.
Catálogos estáticos poblados: **13 posiciones** (con bucket + lado),
**39 stat_types** (los 19 de `STAT_FIELD_MAP` + 20 de `STAT_FIELD_MAP_EXTRA`
del experimento; `goals-conceded` y `cleansheets` marcados
`valid_for = 'goalkeeper_only'`, el resto `'all'`).

**Smoke test — cargó sin errores:**
- **14 jugadores** = los 13 de prueba + **Arnaut Danjuma añadido a
  propósito** (ninguno de los 13 es multi-etapa; Danjuma jugó en Villarreal
  y Girona en 2024/25, así que ejercita ese camino). Está marcado en la
  salida del script.
- **15 `player_team_season`** (Danjuma tiene 2).
- **559 `player_statistics`**, de los cuales **113 imputados a 0**
  (`is_imputed_zero = true`).
- **4 filas de stats solo-portero** (2 porteros × goals-conceded +
  cleansheets), todas con valores reales, ninguna en jugadores de campo.

**Verificado por SQL:** la agregación multi-etapa funciona
(`SUM ... GROUP BY` sobre las 2 etapas de Danjuma → 1539 min, 4 goles,
36 tiros en la temporada); el unique constraint de `player_statistics`
rechaza duplicados; una consulta con forma de "goles/90 por bucket, con
mínimo de 600 min" corre bien.

### Ajustes / notas al topar con datos reales (NO se cambió la estructura)

El esquema aguantó tal cual. Pero al cargar datos reales aparecieron 3
cosas que hay que resolver en Fase 2, ninguna es un cambio de esquema:

1. **`player_team_season.date_from` sale siempre NULL.** Sportmonks (en los
   datos que tenemos: squads + statistics) no da fechas de inicio/fin de
   cada etapa. El unique constraint es `(player_id, team_id, season_id,
   date_from)` tal como se pidió; con `date_from` NULL funciona para
   Danjuma (2 equipos distintos → 2 filas, sin conflicto), PERO **no
   detectaría un jugador con 2 etapas en el MISMO equipo** (cesión y
   vuelta), porque en Postgres `NULL != NULL` en un índice único. Para
   Fase 2: o se consiguen las fechas, o se añade un número de secuencia de
   etapa a la clave.
2. **`players.nationality` guarda el `nationality_id` de Sportmonks como
   texto** (ej. "17"), no el nombre del país. Igual que pasó con
   `position_id` en Fase 0 — hace falta resolver los IDs de país contra la
   tabla de Sportmonks. Lo mismo con `teams.country` (se resolvió solo
   `country_id = 32 → "Spain"` con un mini-mapa).
3. **`players.preferred_foot` queda NULL.** Sportmonks no lo devuelve en el
   include que usamos (`statistics.details.type`). Habrá que ver si otro
   include lo trae, o dejarlo sin dato.

Observación menor: `saves` está como `valid_for = 'all'` (según lo pedido:
solo `goals-conceded` y `cleansheets` son goalkeeper_only), así que a los
jugadores de campo se les imputa `saves = 0`. No contamina nada porque los
percentiles de Fase 3 se calcularán por bucket de posición, pero son ~13
filas de ruido. Si molesta, se puede añadir `saves` a goalkeeper_only.

### Pendientes que entran a Fase 2 (ETL masivo)

- Resolver IDs de Sportmonks a nombres: país (nationality, team country).
- Fechas de etapa (o secuencia) para `player_team_season`.
- `preferred_foot`: buscar include o aceptar sin dato.
- Alembic para migraciones (ahora es `create_all()` a pelo).
- `git init` del proyecto.

---

## 2026-08-30 (tarde) — Ajustes previos a Fase 2 (git, saves, fechas de etapa)

Tres flecos del smoke test, cerrados antes de arrancar el ETL masivo.

**1. `git init`.** `scouting-engine/` es ya un repo git. `.gitignore`
ampliado (`.env`, `__pycache__/`, `*.pyc`, venvs, `raw_data/`, `data/`,
`*.dump`, editor/OS). Primer commit con el estado real del proyecto
(esquema + smoke test + docs), no un commit vacío.

**2. `saves` movido a `valid_for = 'goalkeeper_only'`** en el seed de
`stat_types` (antes `'all'`). Motivo: `saves` siempre es 0 para jugadores
de campo, no tiene sentido imputarlo — eran ~13 filas de ruido.
**Decisión: SÍ relancé el smoke test** (`create_schema --drop` + load),
porque no cuesta nada (solo lee ficheros locales, 0 llamadas a API / 0
cuota Sportmonks) y así la BD de validación refleja el esquema corregido.
Efecto: `player_statistics` 559 → **546**, imputados a 0 113 → **100**,
filas solo-portero 4 → **6** (2 porteros × saves + goals-conceded +
cleansheets). Verificado que `saves` solo cuelga ya de los 2 porteros,
con valores reales (Courtois 77, Unai Simón 48).

**3. Fechas de etapa (`player_team_season.date_from`): EL DATO EXISTE.**
Está en `/players/{id}?include=transfers` (entidad Player, 2000 req/hora).
Devuelve el historial de fichajes del jugador; cada registro trae:
`date`, `from_team_id`, `to_team_id`, `type_id`, `completed`, `amount`.
`type_id`: 218 = Loan, 219 = Transfer, 220 = Free Transfer,
9688 = End of loan.

Ejemplo real (Arnaut Danjuma, la cesión que usamos en el smoke test):
- 2024-06-30 "End of loan": Everton (13) → Villarreal (3477)
- 2024-08-30 "Loan": Villarreal (3477) → Girona (231)
- 2025-06-30 "End of loan": Girona (231) → Villarreal (3477)

→ etapa Villarreal 2024/25 = 2024-06-30 a 2024-08-30; etapa Girona =
2024-08-30 a 2025-06-30. **No hay un campo "inicio/fin de etapa" directo**:
hay que encadenar los fichajes consecutivos (el `to_team` de un fichaje
abre una etapa, la `date` del siguiente la cierra). Cuesta 1 request por
jugador.

**Pendiente de decidir juntos** (no implementado): si en Fase 2 se
incorpora ese include para poblar `date_from`/`date_to` de verdad (1
request extra por jugador con >1 etapa, o por todos), o si se va con la
opción por defecto de añadir un `order_in_season` (número de secuencia de
etapa) a la clave única de `player_team_season` para evitar el problema de
`NULL != NULL`. Como el dato existe, la propuesta pasa a ser: usar los
transfers para las fechas y añadir igualmente `order_in_season` como
respaldo / desempate.

---

## 2026-08-30 (noche) — Fase 2: ETL masivo del roster de LaLiga

**Qué es esto.** El ETL que carga el roster completo de LaLiga 2024/25 en
PostgreSQL, reutilizando el JSON ya descargado en Fase 0
(`../data-experiment/raw_data/sportmonks/`, 762 jugadores) sin volver a
pedir a la API. Es el paso previo a poder calcular percentiles (Fase 3).

**Decisiones de entrada (venían del prompt, no se reabrieron):**
- Reutilizar los datos ya descargados; solo llamar a la API para huecos
  (`--fetch-missing`). No hubo huecos: 762/762 archivos presentes.
- Solo LaLiga por ahora (Segunda será otra pasada del mismo pipeline).
- `order_in_season` (entero por jugador-temporada) en vez de fechas reales
  para el constraint único de `player_team_season`. **NO** se usó
  `include=transfers`.

**Cambios de esquema (`db/models.py`):**
- Nueva columna `player_team_season.order_in_season` (int, NOT NULL,
  default 0). El unique constraint pasa de `(player_id, team_id,
  season_id, date_from)` a **`(player_id, season_id, order_in_season)`**.
  `date_from`/`date_to` se quedan como columnas opcionales sin usar.
- `player_statistics.player_team_season_id` ahora es
  `ON DELETE CASCADE` (el ETL idempotente borra las etapas de un jugador y
  reinserta; sin el cascade, la FK lo impedía).

**Código nuevo:**
- `loaders/schemas.py` — modelos Pydantic del JSON de Sportmonks
  (`PlayerStatsFile` → `PlayerProfile` → `StatEntry` → `StatDetail`).
  Doble función: valida la forma del dato y es el primer borrador del
  mapper JSON→esquema. Un jugador que no valida se registra (agregado por
  tipo de error) y se salta, no tumba el ETL. Probado: rechaza `data`
  ausente, `id` ausente, jugador sin nombre, `team_id` ausente en una
  etapa.
- `loaders/sportmonks_mapping.py` — helpers compartidos (unwrap del
  `value` dict de Sportmonks, `to_number`, `BASE_CODES`, construcción de
  las filas de `player_statistics` con la lógica de imputación de ceros y
  de solo-portero).
- `loaders/etl_laliga.py` — el ETL. Upserts con `INSERT ... ON CONFLICT`
  de Postgres (nada de INSERT ciego). Idempotente: cada jugador se
  procesa "borrar sus `player_team_season` (cascade a stats) + reinsertar",
  commits por lotes de 50. `--dry-run` hace rollback. Stats insertadas en
  bloque por etapa (36s → 7s).
- `loaders/smoke_test_load.py` — ajustado para poner `order_in_season`.

**Resultado del dry-run** (14 jugadores del smoke test, y luego completo):
idéntico al smoke test (14 jug, 15 etapas, 546 stats, 100 imputadas).
Dry-run completo: 762 jug, 0 rechazados, 777 etapas, 27152 stats, 7s.

**Resultado de la carga real completa:**
| métrica | valor |
|---|---|
| jugadores objetivo | 762 |
| cargados | **762** |
| rechazados por validación | **0** |
| jugadores sin ninguna etapa | 0 |
| jugadores multi-etapa | **15** |
| filas `player_team_season` | **777** (747 con 1 etapa, 15 con 2) |
| filas `player_statistics` | **27 152** |
| de ellas `is_imputed_zero=true` | **11 476** (~42 %) |
| `team_ids` fuera de teams.json | 0 |
| tiempo | ~7 s |

**Idempotencia verificada:** relanzado 2 veces → conteos idénticos en la
BD (762 / 777 / 27152 / 11476). Relanzable a media carga sin limpiar nada.

**Verificado por SQL:**
- Los 15 multi-etapa son reales (Danjuma Girona→Villarreal, Aleñá
  Getafe→Alavés, Umar Sadiq Valencia→Real Sociedad, etc.), con
  `order_in_season` 0 y 1 estable (ordenado por team_id).
- `SUM ... GROUP BY player` agrega bien las 2 etapas (Danjuma 1539 min,
  4 goles en la temporada).
- 0 filas `goalkeeper_only` colgando de jugadores de campo.
- Homónimos (Juan Cruz ×2, Dani Rodríguez ×2, Juanpe ×2, David López ×2)
  entran como jugadores distintos por `sportmonks_player_id` — el esquema
  los separa bien (unique por id de proveedor, no por nombre).
- Consulta con forma de Fase 3 ("goles/90 por bucket, mín 900 min"):
  Sørloth 1.15, Mbappé 0.96, Lewandowski 0.91... realista.

**Ajustes sobre la marcha (contados, no en silencio):**
1. **`ON DELETE CASCADE`** en `player_statistics` — el primer intento de
   relanzar el ETL petó con `ForeignKeyViolation` al borrar
   `player_team_season`. Añadido el cascade a nivel de BD.
2. **Inserts de stats en bloque** — la primera versión hacía ~27k
   `execute()` individuales (36 s). Pasado a un `INSERT` multi-fila por
   etapa (7 s).
3. **Resolución de `DATA_EXPERIMENT_DIR`** — desde el worktree, la ruta
   relativa `../data-experiment` no resolvía. El ETL ahora sube
   directorios buscando un hermano `data-experiment/` (funciona desde el
   checkout normal y desde el worktree).

**34 jugadores quedan con `primary_position_id` NULL** — son los que no
tienen `detailed_position_id` en Sportmonks (ya lo sabíamos de Fase 0).
Casi todos de poco minutaje.

**Guard de git / worktree.** Trabajé en un **worktree**
(`.claude/worktrees/fase2-etl`, rama `worktree-fase2-etl`) porque intentar
desactivar el guard con `.claude/settings.json` no lo desactivó a mitad de
sesión. El commit de Fase 2 queda en esa rama. Para traerlo a `master`
(fast-forward, sin conflictos, sale de HEAD de master):
`git merge --ff-only worktree-fase2-etl` desde el checkout principal.

### Pendientes que siguen abiertos (Fase 3+ / mantenimiento)

- Resolver IDs de Sportmonks a nombres: país (`players.nationality`,
  `teams.country` — hoy guardan el id como texto o NULL).
- `players.preferred_foot`: sigue NULL (Sportmonks no lo da en este
  include).
- Alembic para migraciones (ahora `create_all()` + `--drop`).
- `date_from`/`date_to` de `player_team_season`: columnas creadas pero sin
  poblar; si se quisieran, están en `/players/{id}?include=transfers`.
- Segunda División: segunda pasada del mismo ETL con otro `season_id`.
