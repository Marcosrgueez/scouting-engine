# scouting-engine

Motor de scouting de fútbol. Código de producción del proyecto (el
experimento de validación de datos vive aparte, en `../data-experiment/`).

**Fase actual: 3 — normalización per-90 + percentiles por posición.**
Todavía NO hay Player Role Score con pesos (Fase 4). Segunda División será
una segunda pasada del mismo ETL cuando escale.

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

# ETL masivo (Fase 2): cargar el roster completo de LaLiga.
python -m loaders.etl_laliga --dry-run --limit 14   # prueba rapida
python -m loaders.etl_laliga --dry-run              # dry-run completo (rollback)
python -m loaders.etl_laliga                        # carga real (idempotente)

# Percentiles (Fase 3): normalizar per-90 y rankear por bucket de posicion.
python -m analysis.percentiles --dry-run            # calcula y hace rollback
python -m analysis.percentiles                      # umbral por defecto 900 min
python -m analysis.percentiles --min-minutes 750    # el umbral es un parametro
```

## Estructura

```
db/
  database.py        engine + Session (lee DATABASE_URL del .env)
  models.py          los 9 modelos SQLAlchemy
  seed_catalogs.py   datos estáticos de positions y stat_types
  create_schema.py   create_all() + seed (sin Alembic todavía)
loaders/
  schemas.py            modelos Pydantic del JSON de Sportmonks (validacion + mapper)
  sportmonks_mapping.py  helpers JSON -> esquema interno (compartidos)
  smoke_test_load.py     Fase 1: carga puntual de 13 jugadores
  etl_laliga.py          Fase 2: ETL masivo del roster, idempotente
analysis/
  percentiles.py         Fase 3: per-90 + percentiles por bucket, idempotente
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

## Esquema

Catálogos: `competitions`, `seasons`, `teams`, `positions`, `stat_types`.
Entidades: `players`, `player_team_season`, `player_statistics`.
Derivado (Fase 3): `player_percentiles`.

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
