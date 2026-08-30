# scouting-engine

Motor de scouting de fútbol. Código de producción del proyecto (el
experimento de validación de datos vive aparte, en `../data-experiment/`).

**Fase actual: 1 — esquema de PostgreSQL.** Todavía NO hay pipeline de
carga masiva (Fase 2) ni cálculo de percentiles (Fase 3).

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

# Smoke test: cargar los 13 jugadores de prueba ya validados:
python -m loaders.smoke_test_load
```

## Estructura

```
db/
  database.py        engine + Session (lee DATABASE_URL del .env)
  models.py          los 8 modelos SQLAlchemy
  seed_catalogs.py   datos estáticos de positions y stat_types
  create_schema.py   create_all() + seed (sin Alembic todavía)
loaders/
  smoke_test_load.py carga puntual de 13 jugadores desde ../data-experiment
```

## Esquema

Catálogos: `competitions`, `seasons`, `teams`, `positions`, `stat_types`.
Entidades: `players`, `player_team_season`, `player_statistics`.

Puntos de diseño que vienen del experimento de Fase 0
(`../data-experiment/docs/DECISIONS.md`):

- **Fuente única de estadísticas: Sportmonks.** `stat_types.source_provider`
  por defecto `sportmonks`. `players.apifootball_player_id` se guarda solo
  como referencia cruzada.
- **Multi-etapa:** `player_team_season` permite varias filas por
  (jugador, temporada) — cesiones / traspasos dentro de la liga. Las stats
  cuelgan de cada etapa; la agregación se hace con `SUM ... GROUP BY`.
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
