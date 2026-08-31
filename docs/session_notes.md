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

---

## 2026-08-30 (cierre Fase 2) — merge a master + datos para elegir umbral de minutos

**1. Merge.** El trabajo de Fase 2 ya está en `master` (fue un
fast-forward de `worktree-fase2-etl`, hecho la sesión anterior):
`820eb3d` (chore: desactivar guard de worktree) + `0e755ff` (Fase 2 ETL)
sobre `365a108` (Fase 1). Working tree limpio. Rama del worktree borrada,
`.claude/worktrees/fase2-etl/` eliminado del disco. Queda un
`.git/worktrees/fase2-etl/` (metadatos obsoletos) que OneDrive tiene
bloqueado — inocuo (`git worktree list` ya no lo muestra); se limpia solo
en el próximo `git worktree prune` cuando suelte el lock.
**Aviso: OneDrive está sincronizando `.git/` — conviene excluir esa
carpeta de OneDrive; sincronizar un repo git puede corromperlo.**

**2. Umbral de minutos — datos, decisión PENDIENTE.** El "900 min" de la
query de verificación de Fase 2 fue solo un ejemplo, NO un umbral elegido.
En Fase 4 se anotó "600, tentativo". Jugadores dentro/fuera por bucket
según el corte (minutos = suma de `minutes-played` de todas sus etapas):

| bucket | total | >=600 | >=750 | >=900 | mediana min |
|---|---|---|---|---|---|
| portero | 94 | 28 | 24 | 24 | 0 |
| central | 130 | 76 | 69 | 63 | 870 |
| lateral | 113 | 68 | 63 | 57 | 910 |
| centrocampista | 180 | 108 | 101 | 96 | 1016 |
| extremo | 123 | 61 | 57 | 53 | 597 |
| delantero | 88 | 57 | 47 | 43 | 860 |
| (sin posición) | 34 | 3 | 3 | 3 | 0 |
| **TOTAL** | **762** | **401** | **364** | **339** | — |

176 jugadores tienen 0 minutos. Observaciones para decidir en Fase 3:
- **Porteros:** caída brutal (28/94 a >=600, y ya no baja más a 900). El
  pool de porteros con minutos es inherentemente ~24-28; puede necesitar
  umbral propio o asumir muestra pequeña.
- **Extremos:** mediana 597, justo en la línea de 600. Es la posición que
  más sufre cualquier corte (rotan mucho): 61->53 de 600 a 900.
- **Delanteros:** 57->43 de 600 a 900 (-25 %). También rotación alta.
- **Centrocampistas:** los más robustos (mediana 1016), 108->96.
- **(sin posición):** solo 3 pasan cualquier corte; además no pueden
  entrar en percentiles por bucket (no tienen posición).

Decisión del umbral: en el siguiente prompt.

---

## 2026-08-30 (noche) — Fase 3: normalización per-90 + percentiles por posición

**Qué es esto.** Convertir las estadísticas crudas cargadas en Fase 2 en
algo comparable entre jugadores: valor por 90 minutos, y percentil dentro
del bucket de posición. Es el paso previo al Player Role Score (Fase 4).

**Decisión de diseño (consultada): tabla `player_percentiles` poblada por
función parametrizada, NO vista materializada.** Motivo principal: el
umbral de minutos tiene que ser un parámetro revisable, y una matview lo
cocería en su definición. Además permite recálculo scoped por
liga/temporada cuando escale.

**Umbral de minutos = 900** (10 partidos completos, convención estándar).
Vive como parámetro de `analysis.percentiles.recompute(min_minutes=900)` /
`--min-minutes`, no como constante ni columna de config. Se guarda en cada
fila como `min_minutes` solo por provenance.

**Cambios de esquema (`db/models.py`):**
- `stat_types` +2 columnas: `normalization` (`per90`/`raw`/`none`) y
  `direction` (`higher_better`/`lower_better`).
- Nueva tabla `player_percentiles`: (player_id, season_id, competition_id,
  stat_type_id, position_bucket, metric_value, percentile, pool_size,
  min_minutes, computed_at). Unique (player_id, season_id, stat_type_id).
  `ON DELETE CASCADE` desde players.

**Qué se convierte a per90 y qué no** (en `stat_types.normalization`):
- **`per90` (35 stat_types)** — todos los contadores: goles, asistencias,
  tiros, entradas, intercepciones, pases, centros, despejes, duelos,
  regates, faltas, tarjetas, balones largos, grandes ocasiones, saves,
  goles encajados, porterías a cero, etc.
- **`raw` (2)** — `accurate-passes-percentage` (ya es un %) y `rating`
  (media 0-10). Entre etapas de un multi-equipo se hace **media ponderada
  por minutos**, no suma. Verificado con Danjuma: Girona 6.84 (1336') +
  Villarreal 7.14 (203') → 6.88. ✓
- **`none` (2)** — `minutes-played` (es el propio umbral) y `appearances`
  (disponibilidad, no rendimiento). No entran en el cálculo.

**Percentil**: `PERCENT_RANK` dentro de
`(season, competition, position_bucket, stat_type)`, sobre jugadores con
≥900 min, **orientado** con `direction` → **100 = mejor de su bucket
siempre** (para `lower_better` como tarjetas/pérdidas/goles-encajados se
invierte a `1 - percent_rank`). Ceros imputados cuentan como 0.
`goals-conceded`/`cleansheets`/`saves` (`goalkeeper_only`) solo dentro del
bucket portero.

**Jugadores en el cálculo final (336, de los 339 con ≥900 min; 3 quedan
fuera por no tener posición):**

| bucket | jugadores | filas | métricas |
|---|---|---|---|
| portero | 24 | 888 | 37 (34 + 3 solo-portero) |
| central | 63 | 2142 | 34 |
| lateral | 57 | 1938 | 34 |
| centrocampista | 96 | 3264 | 34 |
| extremo | 53 | 1802 | 34 |
| delantero | 43 | 1462 | 34 |
| **TOTAL** | **336** | **11 496** | |

Idempotente (2 pasadas → 11 496 filas idénticas). ~0.5 s. `player_percentiles`
tiene `percentile` en [0,100], sin nulos, sin fuera de rango.

**Sanity check — tiene sentido futbolístico:**

| jugador | métrica | valor/90 | percentil | ¿ok? |
|---|---|---|---|---|
| Mbappé (del) | goles | 0.96 | **98** | ✓ |
| Mbappé | regates exitosos | 2.47 | **100** | ✓ |
| Mbappé | grandes ocasiones falladas (lower_better) | 0.96 | **2** | ✓ falla muchas |
| Lewandowski (del) | goles | 0.91 | 93 | ✓ |
| Pedri (medio) | pases clave | 2.14 | 94 | ✓ |
| Pedri | pases | 82.9 | 97 | ✓ |
| Pedri | pérdidas (lower_better) | 1.15 | 22 | ✓ pierde bastante |
| Lamine Yamal (ext) | asistencias | 0.44 | **100** | ✓ |
| Lamine Yamal | regates exitosos | 4.84 | **100** | ✓ |
| Unai Simón (por) | goles encajados (lower_better) | 0.62 | **100** | ✓ Athletic encajó poco |
| Unai Simón | porterías a cero | 0.48 | 96 | ✓ |

**Caveats confirmados (NO son bugs — límites del dato de temporada crudo):**
1. **Volumen defensivo por-90 infravalora a centrales de equipos
   dominadores.** Rüdiger sale en percentil 2-8 en entradas /
   intercepciones / duelos ganados, no porque sea mal defensor sino
   porque el Madrid tiene el balón y el rival casi no llega a su zona.
   Ajuste por posesión = mejora futura (Fase 4 lo mitiga con pesos, pero
   no lo arregla del todo).
2. **`saves` per-90 de un portero depende de los tiros que recibe.** Unai
   Simón sale bajo en paradas (9º percentil) porque el Athletic defendía
   bien, no porque pare mal. Sin "tiros a puerta recibidos" no hay % de
   paradas. `goals-conceded` y `cleansheets` sí son informativos.
3. **PERCENT_RANK amontona empates en los extremos.** ~20 % de las filas
   están exactamente en 0 o 100 — sobre todo métricas irrelevantes para
   la posición (goles de un central → muchos empatados a 0 → todos
   percentil 0) y `lower_better` donde casi todos tienen 0 (rojas → casi
   todos percentil 100). Es comportamiento estándar de PERCENT_RANK; los
   pesos de Fase 4 sobre métricas relevantes esquivan el problema.

**Código nuevo:** `analysis/` (paquete nuevo para cálculos derivados) con
`analysis/percentiles.py`. `db/seed_catalogs.py` reescrito con las 2
columnas nuevas. `db/models.py` +1 tabla +2 columnas.

**Pendientes (Fase 4+):** Player Role Score con pesos (siguiente prompt,
`docs/roles_fase4_mapping.md` ya tiene el mapa rol→campos); ajuste por
posesión para stats defensivas; % de paradas si algún día hay tiros
recibidos; Alembic.

## 2026-08-30 — Fase 5: Player Role Score con pesos

(El README y `data-experiment/docs/roles_fase4_mapping.md` llamaban a esta
fase "Fase 4". Es lo mismo: el Player Role Score. Numeración unificada a
"Fase 5" según el roadmap del proyecto.)

**Qué se construyó:** score de encaje 0-100 por rol para los **4 roles
construibles plenos** (`ball_winner`, `deep_lying_playmaker`,
`advanced_playmaker`, `ball_playing_cb`), con desglose por métrica para
explicabilidad.

**Esquema nuevo (`db/models.py`, +5 tablas):**
- `roles` (code, label) — catálogo estático.
- `role_buckets` (role_id, bucket) — tabla puente; buckets de posición a
  los que aplica cada rol. Se normalizó en vez de usar un array.
- `role_weights` (role_id, stat_type_id, weight, tier) — pesos. `tier`
  (`core`/`support`/`context`) es **informativo**; el cálculo usa solo
  `weight`. 30 filas (7+7+6+10).
- `player_role_scores` (player_id, season_id, role_id, position_bucket,
  score, total_weight, metrics_used, min_minutes) — único (player, season,
  role).
- `player_role_score_breakdown` (player_role_score_id, stat_type_id, tier,
  percentile, weight, contribution) — una fila por métrica.

Catálogo poblado en `db/seed_catalogs.py` (`seed_roles`, idempotente).
Pesos por nivel: núcleo 3, apoyo 1.5, contexto 0.5.

**Cálculo (`analysis/role_scores.py`, idempotente DELETE+INSERT, ~0.3 s):**
`score = SUM(percentil × peso) / SUM(peso)`, ya en [0,100]. Una sola
sentencia SQL con CTE data-modifying (`INSERT ... RETURNING`) que escribe
score y desglose en la misma pasada. Verificado: `SUM(contribution) /
SUM(weight)` sobre el breakdown reproduce el `score` en las 524 filas
(0 discrepancias > 0.02).

**Decisión sobre métricas faltantes por jugador — EXCLUIR y renormalizar
(NO imputar 50):**
Si a un jugador le falta el percentil de una métrica del rol, esa métrica
se cae del numerador y del denominador; el peso total se renormaliza sobre
lo disponible. NO se imputa percentil 50.
- *Por qué:* los percentiles de Fase 3 ya imputan los ceros que Sportmonks
  omite **antes** de rankear, así que un percentil bajo ya significa "este
  jugador hace poco de esto". Un percentil **ausente** significa otra cosa:
  falta de dato (una liga/temporada futura donde la métrica no se recoge).
  Imputar 50 afirmaría "es mediano en X" sin evidencia y sesgaría el score
  compuesto hacia el centro justo donde no sabemos nada. Renormalizar es
  cómo debe degradar una media ponderada.
- *Guarda:* si el peso disponible < 60 % del peso total del rol, no se
  emite fila (un score renormalizado sobre <60 % de la señal no es
  comparable). `MIN_WEIGHT_COVERAGE = 0.60` en el módulo.
- *Impacto hoy:* **nulo.** Sobre LaLiga 2024/25 la cobertura es del 100 %
  para las 18 métricas de los 4 roles en todos los buckets (la imputación
  de ceros de Fase 3 garantiza una fila por jugador y métrica). 0
  jugadores descartados, 0 con huecos. La política solo importa al escalar
  a más ligas.

**Cobertura del cálculo:**

| rol | buckets | jugadores | media | min | max |
|---|---|---|---|---|---|
| Ball Winner | central+centro+lateral | 216 | 50.0 | 12.1 | 90.1 |
| Deep-Lying Playmaker | centrocampista | 96 | 49.9 | 8.2 | 96.6 |
| Advanced Playmaker | centro+extremo | 149 | 49.4 | 3.4 | 97.4 |
| Ball Playing CB | central | 63 | 50.0 | 15.5 | 78.4 |

524 filas de score, **269 jugadores distintos** (todos los de bucket
central/centro/lateral/extremo con ≥900 min; delanteros y porteros no
reciben score en ninguno de los 4 roles, correcto). 3708 filas de
desglose. Idempotente (2 pasadas → cifras idénticas).

**Sanity check — tiene sentido futbolístico:**

| jugador | rol | score | lectura |
|---|---|---|---|
| Eduardo Camavinga | Ball Winner | **90.1** | ✓ entradas y duelos percentil 100, intercepciones 91 |
| Martín Zubimendi | Ball Winner **69.5** / DLP 54.3 / **AP 28.6** | ✓ pivote que roba y distribuye, NO crea ocasión (pases clave pctl 20) |
| Luka Modrić | Deep-Lying Playmaker | **96.6** | ✓ volumen + balón largo ganado; AP 86, BW 38 |
| Aurélien Tchouaméni | BW 67.8 / DLP 57.2 / **AP 3.4** | ✓ destructor puro, cero creación en último tercio |
| Isco | Advanced Playmaker | **97.4** | ✓ asistencias y pases clave pctl 100, grandes ocasiones creadas 96 |
| Éder Militão | Ball Playing CB | **71.8** | ✓ balón largo ganado pctl 90, precisión 77; despejes pctl 11 = caveat de posesión (CB del Madrid) pero el rol no lo penaliza |
| Antonio Rüdiger | **BPCB 55.8** / BW 15.0 | ✓ el caveat de posesión hunde Ball Winner (volumen defensivo per90 bajo); BPCB lo rescata vía pase |

El contraste que se pidió se cumple: Zubimendi y Tchouaméni salen
altos-medios en Deep-Lying Playmaker por volumen de pase pero se desploman
en Advanced Playmaker por falta de creación de ocasión. El caveat conocido
de Fase 3 (volumen defensivo per90 infravalora a centrales de equipos
dominadores) reaparece en Ball Winner; los pesos de Ball Playing CB lo
esquivan al apoyarse en el pase.

**Caveats:**
1. **`PERCENT_RANK` amontona empates en 0/100** (heredado de Fase 3). En
   métricas núcleo relevantes al rol el efecto es menor, pero p. ej.
   `assists`/`key-passes` de Isco entran como 100 exacto. El score
   resultante sigue siendo sano.
2. **El caveat de posesión no se corrige aquí.** Ajuste por posesión para
   stats defensivas sigue pendiente (mejora futura, ya anotada en Fase 3).
3. **Los pesos son una hipótesis de diseño, no un modelo validado contra
   criterio de ojeadores** (igual que la taxonomía de Fase 4). Se pueden
   reajustar sin tocar el pipeline: solo `db/seed_catalogs.py` + recrear
   el catálogo + relanzar `analysis.role_scores`.

**Código nuevo:** `analysis/role_scores.py`. `db/models.py` +5 tablas +1
constante (`ROLE_TIERS`). `db/seed_catalogs.py` +`seed_roles`. README +
sección "Player Role Score".

**Pendientes (Fase 6+):** Similarity Engine (Fase 6); Tactical Fit Score
(Fase 8); ajuste por posesión; reajuste de pesos tras validación con
ojeador; Alembic (5 tablas nuevas creadas con `create_all`, sin migración).

## 2026-08-30 — Fase 6: Player Similarity Engine

**Qué se construyó:** para cada jugador, el top-20 de jugadores
estadísticamente más similares dentro de su mismo bucket de posición y
temporada. Tabla `player_similarity`.

**Decisión previa consultada (metricas del vector):** la Fase 5 solo tiene
filtro de métricas para los buckets con rol (central/centro/lateral/
extremo), y para lateral serían solo 7 defensivas → dos laterales
ofensivo/defensivo saldrían idénticos. Se eligió **usar TODAS las métricas
con percentil del bucket** (34 de campo, 37 portero). Cubre los 336
jugadores del pool de Fase 3 (incluidos 43 delanteros y 24 porteros que no
tienen rol en Fase 5).

**Esquema nuevo (`db/models.py`, +1 tabla):**
`player_similarity` (player_id, similar_player_id, season_id,
position_bucket, similarity_score `NUMERIC(8,6)`, rank 1-20, n_features,
min_minutes). Único `(player_id, similar_player_id, season_id)`. CHECKs:
`player_id <> similar_player_id`, rank 1-20, score 0-1. La tabla **NO es
simétrica**.

**Cálculo (`analysis/similarity.py`, ~2 s):**
- Vector = percentiles per90 crudos `[0,100]` de `player_percentiles`,
  todas las métricas del bucket. Cobertura Fase 3 = 100 % dentro de cada
  bucket (34/34 campo, 37/37 portero) → vectores alineados y completos,
  sin manejo de dimensiones faltantes.
- **Cosine similarity** sobre el vector crudo. Todo positivo → sim en
  `(0,1]`. Una sola sentencia SQL: `vec` → `norm` (magnitud por jugador)
  → `pairs` (self-join por stat_type dentro de bucket+season, dot
  product) → `sim` (dot / (‖a‖·‖b‖)) → `ranked` (ROW_NUMBER por jugador)
  → INSERT top-20.
- Solo dentro del mismo bucket (join exige `position_bucket` igual).
  Verificado: 0 matches cross-bucket.

**Idempotencia: DELETE scoped + INSERT** (igual que Fases 3 y 5). NO
upsert: el top-20 de un jugador puede cambiar de miembros entre pasadas y
un upsert dejaría filas viejas colgando. 2 pasadas → 6720 filas idénticas.

**Filtros de edad y lado = parámetros de CONSULTA, no del cálculo.** Se
aplican con `WHERE` al leer la tabla ya calculada (join a `birth_date` /
`positions.lado`). La similitud entre dos jugadores no cambia según el
filtro posterior. Confirmado: filtrando "similares a Lamine Yamal" a
sub-23 o a lado izquierda, `similarity_score` y `rank` no cambian — solo
se subsetea el top-20 (quedan huecos en el rank original). `--explain
NOMBRE` en el módulo imprime el top-20 ya calculado de un jugador.

**Fuera de alcance (documentado como pendiente):** pie dominante
(`preferred_foot` NULL en el 100 % del roster) y valor de mercado (sin
fuente). Ningún filtro puede apoyarse en ellos todavía.

**Cobertura:**

| bucket | jugadores | filas | features | sim media | sim min | sim max |
|---|---|---|---|---|---|---|
| portero | 24 | 480 | 37 | 0.761 | 0.598 | 0.930 |
| central | 63 | 1260 | 34 | 0.790 | 0.575 | 0.939 |
| lateral | 57 | 1140 | 34 | 0.806 | 0.596 | 0.943 |
| centrocampista | 96 | 1920 | 34 | 0.841 | 0.669 | 0.967 |
| extremo | 53 | 1060 | 34 | 0.813 | 0.613 | 0.942 |
| delantero | 43 | 860 | 34 | 0.791 | 0.611 | 0.947 |
| **TOTAL** | **336** | **6720** | | | | |

Los 336 jugadores tienen exactamente 20 filas. rank ∈ [1,20], score ∈
[0,1], 0 self-matches, 0 cross-bucket.

**Sanity check — tiene sentido futbolístico (top-5):**

| jugador | top-5 similares | lectura |
|---|---|---|
| Pedri | Sergi Darder, De Paul, Modrić, Arda Güler, Pablo Barrios | ✓ mediapunta/interior creativo |
| Zubimendi | Tchouaméni, Barrenechea, Pathé Ciss, Valverde, Ander Guevara | ✓ pivote posicional (coincide con Fase 5: Zubimendi≈Tchouaméni) |
| Militão | Lenglet, Javi Rodríguez, Lejeune, Diego Llorente, Kike Salas | ✓ central que juega |
| Lamine Yamal | Pépé, Moleiro, Vinicius, Kubo, Raphinha | ✓ extremo regateador |
| Lewandowski | Sørloth, Budimir, Kike García, Mbappé, Abel Ruiz | ✓ '9' de área/referencia |

**El check que se pidió (lateral ofensivo vs defensivo) — pasa:**

| jugador (perfil) | top-5 similares | ¿aparece el opuesto? |
|---|---|---|
| Sergio Gómez (LI ofensivo, centros p98) | Miguel Gutiérrez, Koundé, Lucas Vázquez, Rațiu, Molina | Reinildo/Aramburu NO en su top-20 |
| Reinildo (LI defensivo puro, centros p5) | Iván Balliu, El Hilali, Aramburu, Carmona, Jesús Vázquez | Sergio Gómez NO en su top-20 |

**Caveats:**
1. **Cosine sobre percentiles crudos agrupa los scores alto** (top-1 ~0.9;
   casi nadie por debajo de 0.6). Es esperable: todos los vectores viven
   en el ortante positivo. El *ranking* discrimina bien (ver checks); los
   valores absolutos no son una "probabilidad de ser el mismo jugador".
   Si en Fase 8 se quiere más separación, centrar en 50 (≈correlación) es
   la palanca — pero entonces el score puede ser negativo y habría que
   reescalar; se dejó fuera por el rango 0-1 del esquema y porque el
   ranking ya es sano.
2. **Hereda el caveat de posesión de Fase 3.** Un central de equipo
   dominador se parece a otros centrales de equipo dominador en parte por
   el contexto de su equipo, no solo por su estilo.
3. **`PERCENT_RANK` amontona empates en 0/100** (Fase 3): dos jugadores
   con 0 en las mismas métricas irrelevantes a su posición ganan algo de
   similitud artificial. Efecto pequeño frente a las métricas con varianza.

**Código nuevo:** `analysis/similarity.py`. `db/models.py` +1 tabla.
README + sección "Player Similarity Engine".

**Pendientes (Fase 7+):** Team Style Profile (Fase 7); Tactical Fit Score
(Fase 8); `preferred_foot` y valor de mercado (bloquean filtros de pie y
presupuesto); ajuste por posesión; Alembic (6 tablas ya creadas con
`create_all`, sin migración).

## 2026-08-30 — Fase 7: Team Style Profile

Precedida por la investigación de endpoints (ver
`data-experiment/docs/fase7_fixtures_investigation.md`).

**Catálogo elegido: `team_stat_types` nuevo, NO reutilizar `stat_types`.**
Motivo: aunque 9 de los 15 codes coinciden (`passes`, `tackles`,
`interceptions`, `fouls`, `shots-total`, `shots-on-target`,
`total-crosses`, `accurate-crosses`, `successful-dribbles`), la entidad y
la unidad son distintas — aquí es un **total de un equipo en un partido**,
en `stat_types` un **per-90 de temporada de un jugador** — y las columnas
de metadata de `stat_types` (`normalization` per90/raw/none, `direction`
higher/lower_better, `valid_for` goalkeeper_only) no tienen sentido para
una stat de equipo. Un solo `stat_type_id` tendría que significar dos
cosas según quién lo referencie. `team_stat_types` tiene su propia
metadata: `unit` (count/percentage, decide la imputación) y `stat_group`
(offensive/defensive/possession, para Fase 8). Precedente: el esquema ya
separa `positions` de `stat_types` en vez de una tabla "atributos" única.

**Esquema (+3 tablas):**
- `team_stat_types` — 15 codes (los fiables en 50/50 partidos de la
  muestra). Fuera: `throwins`/`goals-kicks` (ruido situacional),
  `duels-won`/`assists` (casi vacíos por partido, ~9/50).
- `team_fixtures` — 1 fila por (equipo, partido): `sportmonks_fixture_id`
  (único con `team_id`), `venue`, `formation` (string, NULL si falta),
  `goals_for`/`goals_against` (**de `scores[]` CURRENT, nunca de
  statistics**), `result` (derivado), `starting_at` (provenance).
- `team_fixture_statistics` — `value`, `is_imputed_zero`, `is_conceded`
  (false = propia, true = misma stat del rival en ese partido). Único
  `(team_fixture_id, team_stat_type_id, is_conceded)`.

**ETL (`loaders/etl_team_fixtures.py`):**
- Descarga bulk paginada: 8 peticiones (`per_page=50`, 380/50) para toda
  la temporada. JSON crudo en
  `data-experiment/raw_data/sportmonks/fixtures/page_NN.json` (17 MB en
  total — sin `lineups`, que no usa el esquema y multiplicaba el tamaño
  ~20×).
- `--offline` (solo caché) / `--refetch` (fuerza descarga).
- Imputación de ceros: 0 explícito en stats `count` ausentes cuando el
  partido sí tiene estadísticas; las `percentage` no se imputan (si faltan
  no hay fila) — misma lógica que `BASE_CODES` en la Fase 2.
- **Idempotencia: DELETE scoped por `season_id` + cascade + INSERT.** No
  upsert: el set de stats presentes de un partido puede cambiar entre
  descargas y un upsert dejaría filas viejas. 2 pasadas → cifras
  idénticas.

**El cruce se sostiene sobre los 380 partidos** (no solo los 4 de la
muestra):
- 380/380 fixtures cargados, 0 sin formación de algún equipo, 0 sin stats
  de equipo, 0 `team_id` huérfano, 0 partidos sin marcador limpio.
- `participants[].id == lineups.team_id == formations.participant_id ==
  statistics.participant_id == scores.participant` (todo el mismo ID).
- 760 `team_fixtures` (380 local + 380 visitante), cada equipo 38 PJ,
  `sum(goals_for) == sum(goals_against) == 995`, wins == losses (283),
  ventaja de campo visible (169 victorias locales vs 114 visitantes).
- 22 800 `team_fixture_statistics` (760 × 30 = 15 stats × 2 perspectivas),
  **solo 4 imputadas** (todas `accurate-crosses` = 0). Verificado:
  `is_conceded=true` coincide exactamente con el valor propio del rival
  (0 discrepancias).

**Umbral de agregación: ≥5 partidos por formación** (`HAVING count(*) >=
5`, filtro de consulta, no almacenado). Por debajo, la V/E/D y las medias
son ruido de calendario (una formación jugada 3 veces puede ir 3-0-0 por
suerte). Análogo al criterio de minutos de jugador (900 min ≈ 10/38
partidos) pero algo menos estricto porque aquí se agregan stats de partido
completo, no se normalizan eventos escasos. 78/123 combos equipo-formación
(63%) caen por debajo — son la cola de formaciones puntuales.

**Tabla de validación (formaciones con ≥5 PJ, temporada 24/25):**

| equipo | formación | PJ | V-E-D | GF | GA | pos% | prec% | tiros f/c |
|---|---|---|---|---|---|---|---|---|
| FC Barcelona | 4-2-3-1 | 29 | 22-2-5 | 2.52 | 0.97 | 68.4 | 88.0 | 18.0/7.9 |
| FC Barcelona | 4-3-3 | 8 | 5-2-1 | 3.13 | 1.38 | 70.4 | 89.4 | 15.3/8.0 |
| Real Madrid | 4-2-3-1 | 15 | 10-3-2 | 2.47 | 1.27 | 59.9 | 89.8 | 17.5/11.0 |
| Real Madrid | 4-4-2 | 11 | 6-2-3 | 1.45 | 1.09 | 58.1 | 88.3 | 15.9/11.2 |
| Real Madrid | 4-3-3 | 8 | 6-1-1 | 2.38 | 0.75 | 65.6 | 90.1 | 16.5/10.3 |
| Atlético de Madrid | 4-4-2 | 28 | 16-6-6 | 1.75 | 0.89 | 53.1 | 84.6 | 12.2/10.5 |
| Getafe | 4-4-2 | 21 | 8-4-9 | 1.00 | 1.10 | 40.7 | 67.0 | 11.2/10.2 |
| Getafe | 4-2-3-1 | 8 | 2-2-4 | 0.88 | 0.75 | 45.9 | 72.3 | 12.8/7.5 |
| Getafe | 4-1-4-1 | 6 | 1-2-3 | 0.83 | 1.17 | 34.3 | 64.8 | 9.5/10.8 |

Tiene sentido a ojo: Barça dominador (68-70% posesión, 88% precisión,
+10 tiros de diferencia), Atlético 4-4-2 casi fijo y sólido atrás
(Simeone), Getafe pragmático (34-46% posesión, 64-72% precisión —
Bordalás), Madrid rotando 3 formas y 4-3-3 la mejor estadísticamente.

**Caveats:**
1. **Sin xG** a nivel de partido (include `xgfixture` = 403, plan no lo
   cubre). El perfil se apoya en tiros por zona (`shots-insidebox` /
   `-outsidebox`) como proxy de calidad de ocasión.
2. **La formación de Sportmonks es la de inicio**, no refleja cambios de
   sistema dentro del partido.
3. **Los porcentajes concedidos** (`ball-possession` is_conceded, etc.)
   son redundantes con los propios (posesión concedida = 100 − propia);
   se guardan igual por consistencia del modelo `is_conceded`. Los
   `count` concedidos (tiros, córners recibidos…) sí son señal defensiva
   nueva.

**Código nuevo:** `loaders/etl_team_fixtures.py`. `db/models.py` +3
tablas +4 constantes. `db/seed_catalogs.py` +`seed_team_stat_types` (15).
README + sección "Team Style Profile".

**Pendientes (Fase 8+):** Tactical Fit Score (Fase 8, cruza rol de jugador
× estilo de equipo); posible descarga de `lineups` por partido si Fase 8
la necesita (8 peticiones); ajuste por posesión para stats defensivas de
jugador; Alembic (9 tablas ya creadas con `create_all`).

## 2026-08-30 — Fase 8: Tactical Fit Score (cierra el núcleo analítico)

`tactical_fit = w_role·role_score + w_style·style_compatibility`, ambos en
[0,100], `w_role+w_style=1` → score en [0,100]. Pesos **70/30 por defecto
como parámetro** (`--w-role`/`--w-style`). Heurística explícita — sin datos
de evento no se puede *aprender* qué perfil rinde en qué estilo.

**Decisión de almacenamiento (consultada): HÍBRIDO — precalcular la parte
de equipo, calcular el fit bajo demanda.**
- El producto cartesiano jugador×equipo×rol×formación son ~34 k filas de
  `0.7·a + 0.3·b` (+ ~51 k de breakdown, 99 % redundante) que quedarían
  obsoletas al tocar el peso, que por diseño es un parámetro.
- El `role_score` ya está en `player_role_scores` (Fase 5). La parte cara y
  reutilizable (independiente del jugador) son los percentiles de estilo:
  se precalculan en `team_style_axes` (325 filas). El fit en sí es una
  **función parametrizada bajo demanda** (`analysis/tactical_fit.py`),
  mismo patrón "función parametrizada" que los percentiles de Fase 3.
- No se crean las tablas `tactical_fit_scores` / `tactical_fit_breakdown`
  del prompt: son la forma de salida de la función (score +
  role_component + style_component + breakdown por eje).

**Granularidad de pesos: tabla PLANA, todos 1.0** (no tiers). La matriz de
diseño solo especifica **signos** (+/−), no magnitudes, y hay **1-3 ejes
por rol** (vs 7-10 métricas por rol en Fase 5). Tiers (núcleo/apoyo/
contexto) codificarían una jerarquía que el diseño no da → precisión
falsa. La columna `weight` es numeric por si se afina con datos más
adelante.

**Esquema (+2 tablas):**
- `role_style_weights` — catálogo, 7 filas. `(role_id, style_axis, weight,
  direction)`. `direction='negative'` (solo directitud en Deep-Lying
  Playmaker) → en el cálculo se usa `100 − percentil`.
- `team_style_axes` — 325 filas (5 ejes × 65 perfiles = 20 agregados +
  45 formaciones ≥5 PJ). `(team_id, season_id, formation NULL-able,
  style_axis, raw_value, percentile, n_matches, min_matches)`. Único con
  `postgresql_nulls_not_distinct=True` (formación NULL = agregado, único).

**5 ejes de estilo** (todos desde stats propias del equipo, `is_conceded=
false`):
| eje | cálculo |
|---|---|
| possession | media de `ball-possession` |
| pass_accuracy | media de `successful-passes-percentage` |
| crossing_frequency | media de `total-crosses`/partido |
| press_intensity | media de `(tackles + interceptions)`/partido |
| directness | `SUM(long-passes)/SUM(passes) × 100` |

Percentil: método Hazen contra los **20 agregados de equipo** (pool fijo,
también para las filas por formación) → agregados repartidos en [2.5, 97.5],
formaciones interpolan.

**`analysis/team_style.py`** (idempotente DELETE scoped + INSERT, ~0.2 s):
puebla `team_style_axes`. Un solo SQL: pivot de stats por partido → media
por (equipo, formación≥5) y por (equipo) → formato largo → percentil Hazen.

**`analysis/tactical_fit.py`** (función bajo demanda):
`style_compatibility = SUM(pctl_efectivo · peso) / SUM(peso)` donde
`pctl_efectivo = 100−percentil` para ejes `negative`, si no el percentil.
Misma forma de combinar que el Role Score. Devuelve score + componentes +
breakdown por eje. `--by-formation` da una fila por agregado y por cada
formación con muestra. `--explain` imprime el desglose.

**Percentiles de estilo — sanity (agregado, temporada 24/25):**
FC Barcelona posesión p97 / precisión p92 / directitud p2 / presión p2
(Flick, dominador); Getafe posesión p7 / precisión p2 / directitud p97
(Bordalás, directo); Deportivo Alavés presión p97 (más acciones
defensivas); Osasuna centros p97. Todo coherente a ojo.

**Validación del Tactical Fit — los 3 casos pedidos:**

| caso | jugador (role_score) | equipo A (fit) | equipo B (fit) | eje que decide |
|---|---|---|---|---|
| Ball Winner ↑ en presión alta | Camavinga (BW 90.1) | **Dep. Alavés 92.3** (press p97) | **Barça 63.8** (press p2) | `press_intensity` +95 pp de swing en style |
| Deep-Lying Playmaker ↑ en Barça | Pedri (DLP 90.0) | **Barça 91.8** (poss p98, prec p92, direct p2→efectivo 98) | **Getafe 64.3** (poss p8, prec p2, direct p98→efectivo 2) | los 3 ejes refuerzan / arrastran |
| Advanced Playmaker ↑ con centros | Isco (AP 97.4) | **Osasuna 97.5** (centros p97) | **Leganés 69.0** (centros p2) | `crossing_frequency` |

El desglose (`--explain`) explica cada caso: p.ej. Pedri en Getafe →
`directness` bruto 21.6, `dir=−` → percentil 98 pasa a efectivo 2, tira el
style_component a 4.2. Camavinga en Barça → `press_intensity` bruto 20.1
(percentil 2) porque el rival casi no tiene el balón. `--by-formation`:
Pedri DLP en Real Madrid sale mejor en 4-3-3 (style 96.7) que en 4-4-2
(90.0). Peso 50/50: Camavinga BW en Barça baja de 63.8 a 46.3.

**Caveats:**
1. **`press_intensity` no es presión real** (necesita datos de evento /
   PPDA). Mide actividad defensiva total, que correlaciona con MENOS
   posesión → un Ball Winner encaja en equipos de bloque bajo scrappy
   (Alavés, Sevilla), no necesariamente en un pressing alto tipo Klopp.
   Hereda el caveat de posesión de Fase 3.
2. **Advanced Playmaker y Ball Winner tienen un solo eje** de estilo → su
   `style_compatibility` ES ese percentil, sin matices. La matriz de
   diseño lo definió así.
3. **La heurística no está validada contra criterio de ojeadores** (como
   toda la cadena role/similarity). Los pesos y la matriz se reajustan sin
   tocar el pipeline: `db/seed_catalogs.py` + recrear catálogo, o
   argumentos de la función.

**Código nuevo:** `analysis/team_style.py`, `analysis/tactical_fit.py`.
`db/models.py` +2 tablas +2 constantes. `db/seed_catalogs.py`
+`seed_role_style_weights` (7). README + sección "Tactical Fit Score".

**Con esto se cierra el núcleo analítico (Fases 0-8).** Pendientes: backend
FastAPI (Fase 9), frontend (Fase 10); Alembic (11 tablas con `create_all`);
2ª División como 2ª pasada del ETL; validación con ojeador; datos de evento
si algún día se incorporan (desbloquean xG, presión real, Box-to-Box y
Poacher plenos, Pressing Forward).

## 2026-08-31 — Fase 9: API FastAPI

Expone el núcleo analítico (Fases 1-8) por HTTP. **Solo backend** — nada de
frontend (Fase 10).

**Decisiones de entrada (del prompt, no reabiertas):** la API nunca
reimplementa lógica de `analysis/`; alcance solo Fases 1-8 (nada de
potencial ni "Replace Player" como endpoint); Tactical Fit en vivo por
request; sin auth; Swagger activado.

**Estructura (`api/`):**
```
api/
  main.py            FastAPI app, CORS (*), monta routers, / y /health
  dependencies.py    get_db (sesión por request) + AGE_REFERENCE_DATE 2025-05-25
  routers/           players.py teams.py roles.py scouting.py  (thin: validan y delegan)
  services/          players.py teams.py roles.py scouting.py  (queries + llamada a analysis/)
  schemas/           players.py teams.py roles.py scouting.py  (Pydantic req/resp de la API)
```
`services/roles.py` no estaba en el esqueleto del prompt (listaba players/
teams/scouting); se añadió para que `routers/roles.py` tenga su servicio
simétrico. `requirements.txt` +`fastapi==0.115.0` +`uvicorn[standard]==0.30.6`.

**Cómo la API no duplica `analysis/`:**
- `/scouting/tactical-fit` → `analysis.tactical_fit.tactical_fit(db, ...)` tal cual.
- `/players/{id}/similar`, `/roles`, `/players/{id}/roles`, `/players/{id}` (percentiles),
  `/teams/{id}/style` → SELECT sobre las tablas que `role_scores.py` /
  `similarity.py` / `percentiles.py` / `team_style.py` ya poblaron.
- Lo único que se computa nuevo son agregaciones de acceso que ningún
  módulo materializa: minutos totales por jugador (`SUM` de `minutes-played`),
  equipo "actual" (`order_in_season` máx), edad (`age()` de Postgres a fin
  de temporada), y `GROUP BY` sobre `team_fixtures` para las formaciones
  bajo umbral — este último es el patrón de acceso que la Fase 7 diseñó.

**8 endpoints, todos probados contra datos reales (uvicorn local):**

| endpoint | comprobación |
|---|---|
| `GET /players?bucket=centrocampista` | total_count 96 (= pool de Fase 5) |
| `GET /players?bucket=lateral&side=izquierda&age_max=25` | total_count 11, todos izquierda y ≤25 → filtros componen y el total refleja el filtro (paginación correcta) |
| `GET /players/396` (Camavinga) | 34 percentiles; tackles/duels-won p100, interceptions p90.5 = Fase 5 |
| `GET /players/396/roles` | ball_winner 90.12 (= Fase 5), DLP 67.17, AP 65.73 (= Fase 8), con breakdown |
| `GET /players/328/similar` (Sergio Gómez) | top-5 = Fase 6 exacto (M. Gutiérrez, Koundé, L. Vázquez, Rațiu, Molina) |
| `GET /players/328/similar?side=derecha` | solo derecha, ranks con huecos (2,3,4,5,6,9…) → **control de Fase 6: filtrando a un lado no aparece el contrario** |
| `GET /teams/10/style` (Barça) | agregado: posesión p97.5, directitud p2.5, presión p2.5 (= Fase 8); by_formation 4-2-3-1 (29) + 4-3-3 (8); below_threshold 4-1-4-1 (1) |
| `GET /roles` | 4 roles con metric_weights (tier+peso) y style_weights (DLP directness=negative) |
| `POST /scouting/tactical-fit {11, 1}` | **Camavinga Ball Winner en Dep. Alavés (presión p97): FIT 92.33** — idéntico a la validación de Fase 8 |
| `POST /scouting/tactical-fit {10, 1}` | Camavinga Ball Winner en Barça (presión p2): **FIT 63.83** — idéntico a Fase 8 |

**Errores (probados):**
- 404: `/players/99999`, `/teams/999/style`, tactical-fit con `role_id`/`team_id` inexistente.
- 422 automático (Pydantic): body sin `role_id` → `loc: [body, role_id]`.
- 422 con mensaje: tactical-fit con `formation:"5-3-2"` en Barça →
  *"La formación '5-3-2' de 'FC Barcelona' no tiene muestra suficiente
  (mínimo 5 partidos…). Formaciones con perfil: ['4-2-3-1', '4-3-3']…"*.
- Jugador sub-900 (`/players/4`, Januzaj 597') → 200 con `percentiles: []`
  y nota; `/players/4/similar` → `items: []` + nota. Delantero >900
  (`/players/2/roles`, Iago Aspas) → `items: []` + nota (delantero no
  tiene ninguno de los 4 roles).

**Decisión — formaciones bajo el umbral de 5 en `/teams/{id}/style`:** se
**incluyen, marcadas como muestra insuficiente**, en `formations_below_threshold`
(solo `formation` + `n_matches`, sin ejes de estilo). `team_style_axes`
nunca las materializó (Fase 7 filtra en la carga), así que no hay
percentiles que dar; pero omitirlas ocultaría que el equipo también usó
esas formaciones. Se leen de `team_fixtures` por `GROUP BY`.

**Notas:**
- CORS abierto (`allow_origins=["*"]`, `allow_credentials=False`) — el
  frontend de Fase 10 es cliente aparte, sin cookies ni auth que proteger.
- `/scouting/tactical-fit` devuelve TODO el ranking (hasta 216 jugadores,
  ~68 KB para Ball Winner). Sin paginación: el prompt pide "el ranking",
  y el frontend puede recortar. Si crece con más ligas, se añade `limit`.
- Respuesta de percentiles/similar/roles: `Decimal` de la BD se convierte
  a `float` en el servicio antes de serializar.

**Arranque local:** `python -m uvicorn api.main:app --reload` →
`http://127.0.0.1:8000/docs`.

**Código nuevo:** `api/` (17 ficheros). `requirements.txt` +2 deps.
README + sección "API".

**Pendientes (Fase 10+):** frontend; "Replace Player" (Fase 11, reusará
similar + tactical-fit); endpoints de potencial/desarrollo (Fase 12, sin
construir); Alembic; auth si el deploy lo requiere; 2ª División.
