> **Documento de metodología (archivado).** Registro de una investigación o decisión tomada durante el desarrollo. La validación de datos se hizo en un espacio de trabajo aparte (`data-experiment/`, no incluido en este repositorio); las rutas a `reports/`, `raw_data/` y `scripts/*.py` se refieren a ese espacio, no a este repo. Índice de docs: [`docs/README.md`](./README.md).

---

# Investigación previa — Premier League, Serie A, Bundesliga

Mismo criterio que la investigación de Segunda (Fase 12b): comprobar con
datos reales, muestra pequeña, antes de comprometerse a nada. **Nada de ETL
ni de esquema.**

- Fecha: 2026-09-02. Script: `scripts/12_investigate_leagues.py`.
- Crudos: `raw_data/sportmonks/investigate_leagues/{premier,seriea,bundesliga}/`.
- LaLiga 24/25, LaLiga 25/26 y Segunda 25/26 ya cargadas — no se tocan.

---

## 1. Acceso — CONFIRMADO ✅

`/leagues` devuelve las 5 del plan: **Premier League (8), Bundesliga (82),
Serie A (384), La Liga (564), La Liga 2 (567)**. Las tres nuevas resuelven
sin error de suscripción.

## 2. `league_id` / `season_id`

| Liga | league_id | 2025/26 (`finished`) | 2024/25 (`finished`) | 2026/27 |
|---|---|---|---|---|
| **Premier League** | **8** | **25583** ✅ | 23614 ✅ | 28083 (`is_current`) |
| **Serie A** | **384** | **25533** ✅ | 23746 ✅ | 27895 (`is_current`) |
| **Bundesliga** | **82** | **25646** ✅ | 23744 ✅ | 28321 (`is_current`) |

**Las tres tienen la 2025/26 `finished: true`** y la 2026/27 en curso. **No
hace falta usar 2024/25 como referencia** — la 25/26 está cerrada e íntegra
(a diferencia de LaLiga en la investigación original de la Fase 12, cuando
la 25/26 aún no existía).

| Liga | equipos | partidos | estado calendario |
|---|---|---|---|
| Premier League | **20** | **380** | 380/380 FT, 380 con result_info → COMPLETA |
| Serie A | **20** | **380** | 380/380 FT → COMPLETA |
| Bundesliga | **18** | **306** | 306/306 FT → COMPLETA |

Bundesliga: 18 equipos → 306 partidos (18×17), ~19 % menos de calendario y
de roster que una liga de 20.

## 3. Calidad de dato — idéntica a LaLiga, sin diferencia real en ninguna

Muestra de 15 regulares (≥900 min) por liga. Completitud de los 21 campos
que sostienen los 4 roles construibles plenos:

- **Base (6 campos) al 100 %** en las tres: `minutes-played`, `appearances`,
  `passes`, `accurate-passes-percentage`, `rating`, `duels-won`.
- **Núcleo defensivo/pase 93-100 %**: `tackles`, `interceptions`,
  `clearances`, `aeriels-won`, `long-balls`, `long-balls-won`, `key-passes`,
  `successful-dribbles`, `dribble-attempts`.
- **`blocked-shots` ~87 %** en las tres — es el suelo de zero-omission de
  LaLiga (jugadores que bloquearon 0 tiros), no un hueco.
- **`big-chances-created` 67-87 %, `goals` 67-87 %, `assists` 67 %,
  `through-balls` 27-73 %** — el patrón de zero-omission de la Fase 4 sobre
  una muestra con muchos defensas/pivotes.

### Diff exacto de codes vs LaLiga

Único resultado del check "codes presentes en LaLiga y ausentes en toda la
muestra":

| Liga | codes ausentes en la muestra |
|---|---|
| Premier League | `redcards`, `yellowred-cards` |
| Serie A | `yellowred-cards` |
| Bundesliga | `yellowred-cards` |

Son eventos disciplinarios raros: 0 en 15 jugadores es lo esperado (la
completitud de `redcards` en la propia LaLiga es del 13 %; ver
`roles_fase4_mapping.md`). **Ninguno de los dos lo usa ningún rol.**

### `through-balls` SÍ se recoge en las tres (a diferencia de Segunda)

En Segunda, `through-balls` / `through-balls-won` estaban **totalmente
ausentes** — no aparecían ni para un extremo creativo (Adrián Embarba,
3131 min). Aquí **sí aparecen**: verificado con **Charles De Ketelaere**
(Serie A, mediapunta del Atalanta, 2189 min): `through-balls = 7`,
`key-passes = 63`, `big-chances-created = 18`. Los porcentajes bajos de la
muestra son composición (pocos atacantes), no una laguna de dato.

### Impacto en los 4 roles — NINGUNO

Las tres ligas tienen **el conjunto completo de estadísticas de LaLiga**.
El núcleo de los 4 roles está al 87-100 % en las tres (el 87 % es el suelo
de zero-omission de `blocked-shots`, igual que en LaLiga). Con la
imputación de ceros del ETL y los percentiles scoped por competición-
temporada, **los 4 roles son construibles plenos en Premier League, Serie A
y Bundesliga con la misma calidad y los mismos caveats que en LaLiga. Sin
regresión. Ningún rol se ve afectado en ninguna de las tres.**

## 4. Team Style Profile — idéntico a LaLiga

Página 1 de `/fixtures?filters=fixtureSeasons:{sid}&include=participants;formations;statistics.type;scores;state&per_page=50`:

| Liga | 2 formaciones/fixture | stats de ambos equipos | 15 team_stat_types |
|---|---|---|---|
| Premier League | 50/50 | 50/50 | 50/50 (salvo `accurate-crosses` 49/50) |
| Serie A | 50/50 | 50/50 | 50/50 |
| Bundesliga | 50/50 | 50/50 | 50/50 |

El fallo puntual de `accurate-crosses` en 1 fixture de PL es la misma
intermitencia menor que ya se vio en LaLiga. **Sin xG** en ninguna:
`xgfixture` → *"You do not have access to the 'xgfixture' include"* (igual
que LaLiga y Segunda). Team Style funciona igual.

## 5. Dedup de `sportmonks_team_id` entre competiciones

El check sobre las tres muestras + los `teams.json` de LaLiga 24/25, LaLiga
25/26 y Segunda 25/26:

- **20 `team_id` aparecen en >1 competición — todos internos de España**
  (LaLiga 24/25 ↔ 25/26 para clubes que siguen en Primera; LaLiga ↔ Segunda
  para Valladolid/Leganés/Las Palmas). Esperado y ya resuelto por el
  esquema multi-temporada de la Fase 12.
- **Cero colisiones** entre Premier League, Serie A, Bundesliga y España, ni
  entre ellas. Los 58 equipos nuevos (20+20+18) tienen `sportmonks_team_id`
  únicos y disjuntos. El upsert por `sportmonks_team_id` basta, como hasta
  ahora.

## 6. Coste de la carga

Roster estimado (precedente: ~40 entradas de plantilla/equipo; LaLiga 25/26
~800 jugadores, Segunda ~834):

| Liga | equipos | jugadores estimados (peticiones `Player`) |
|---|---|---|
| Premier League | 20 | ~800 |
| Serie A | 20 | ~800 |
| Bundesliga | 18 | ~720 |
| **Total 3 ligas** | 58 | **~2.320** |

Más, por liga: 1 `/leagues` + 1 `/teams/seasons` + ~18-20 `/squads` + ~7-9
páginas de `/fixtures` ≈ **~30**, repartidas en las entidades League / Team
/ Squad / Fixture — nunca son el cuello de botella.

- **Límite: 2.000 peticiones / hora / entidad.** El cuello de botella es
  `Player`. **2.320 > 2.000 → hay que trocear.**
- Precedente: la descarga de Segunda (~834 jugadores) consumió ~800 del
  bucket `Player` (cuota 2000 → 1200), ~40 min de reloj. **Una liga entra
  cómoda en una ventana.**

### Recomendación: **3 ventanas horarias, una liga por ventana**

Riesgo cero: cada liga (~720-800 peticiones `Player`) reproduce exactamente
el patrón ya probado con LaLiga 25/26 y Segunda. ~40 min de descarga por
liga, repartidas en 3 horas de reloj distintas.

Alternativa (2 ventanas): p. ej. Premier + Bundesliga (~1.520 `Player`) en
una, Serie A (~800) en otra. Cabe bajo 2.000 con margen, pero si hay
reintentos o la ventana horaria no está limpia se acerca al límite. Las 3
ventanas son la opción segura.

## 7. Para el diseño de la carga (Fase 13 — NO implementar todavía)

- `scripts/10_fetch_season.py`: ampliar `LEAGUE_TIER` a
  `{8: 1, 82: 1, 384: 1, 564: 1, 567: 2}` (las tres nuevas son tier 1).
- **Sin cambio de esquema** — el soporte multi-competición se cerró en la
  Fase 12b. `etl_laliga.py` ya asigna tier 1 por defecto a cualquier
  `league_id != 567`.
- Nombres de equipo con acentos/umlauts (Köln, Mönchengladbach, München) —
  la BD ya maneja UTF-8 (Valladolid, Leganés funcionan).
- Cada liga = una fila `seasons` nueva (nuevo `sportmonks_season_id`),
  recálculo de `analysis` scoped por `--season-id`, sin contaminación
  cruzada (el PARTITION separa por season+competition).
- El selector del frontend pasará a 4 competiciones — ya agrupa por
  competición vía `<optgroup>`, solo son más opciones.
- Decisión abierta (no técnica): con 5 ligas y sin League Strength
  Coefficient, los rankings siguen sin cruzar competición. Sigue siendo un
  pendiente consciente.

---

## Resumen para decidir el plan de carga

1. **Acceso: las 3 confirmadas.** PL 8 / 25583, Serie A 384 / 25533,
   Bundesliga 82 / 25646 — todas 2025/26 `finished`, calendario completo.
2. **Calidad de dato: idéntica a LaLiga en las tres.** El conjunto completo
   de stats, mismo patrón de zero-omission, sin ausencias reales (solo
   `redcards`/`yellowred-cards` en la muestra, que no usa ningún rol).
   **Los 4 roles construibles plenos, sin regresión, ningún rol afectado.**
3. **Team Style: idéntico.** 15 stat types, 2 formaciones, sin xG.
4. **Tamaños:** PL y Serie A 20 equipos / 380 partidos; Bundesliga 18 / 306.
5. **Dedup: sin colisiones** con España ni entre ellas.
6. **Coste: ~2.320 peticiones `Player` → trocear en 3 ventanas** (una liga
   por hora), replicando el patrón probado de LaLiga/Segunda.
