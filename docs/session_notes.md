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
