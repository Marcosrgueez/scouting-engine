> **Documento de metodología (archivado).** Registro de una investigación o decisión tomada durante el desarrollo. La validación de datos se hizo en un espacio de trabajo aparte (`data-experiment/`, no incluido en este repositorio); las rutas a `reports/`, `raw_data/` y `scripts/*.py` se refieren a ese espacio, no a este repo. Índice de docs: [`docs/README.md`](./README.md).

---

# Decisiones de arquitectura

Registro de decisiones tomadas y su justificación. Entrada nueva al final,
fechada. Una decisión aquí no se revierte sin otra entrada que lo diga.

---

## 2026-08-30 — Sportmonks es la fuente única de verdad para estadísticas de jugador

**Estado:** aceptada.

**Contexto:** el experimento de Fase 0 (`data-experiment/`) validó con datos
reales de LaLiga 2024/25 qué devuelven de verdad Sportmonks v3 y API-Football
(plan gratuito). Resultados en `reports/field_completeness.md` y
`reports/field_comparison.csv`.

**Decisión:**

1. **Sportmonks es la única fuente de estadísticas de jugador.** Todos los
   campos estadísticos que alimenten la taxonomía de roles (Fase 4), el
   cálculo de percentiles (Fase 3) y el scoring salen de Sportmonks.

2. **API-Football queda como fuente de contraste / backup**, no de
   producción. No se combinan campos de los dos proveedores dentro de la
   misma estadística ni del mismo percentil. Si en el futuro se usa
   API-Football, será para un chequeo de sanidad puntual, no como parte del
   pipeline.

3. La temporada de referencia validada es **2024/25** (`FORCE_SEASON_YEAR=2024`).
   En el trial de Sportmonks es la más reciente con datos completos.

**Motivos (todos verificados con datos reales, no supuestos de Fase 0):**

- **`tiros_totales` diverge 30-50 % entre proveedores** por diferencia de
  definición (Lamine Yamal 144 vs 95, Mbappé 161 vs 122, Bellingham 62 vs
  46). Combinar o alternar proveedores en este campo produciría percentiles
  incoherentes.
- **`precision_pases` de API-Football está roto:** `null` en 7 de 13
  jugadores de prueba, y donde trae valor no es un porcentaje
  (Cubarsí "69" cuando su precisión real es 93 %). Sportmonks da un %
  limpio y presente al 100 % (rango 66-94 % en la muestra).
- **Sportmonks es más rico:** ~49 métricas por jugador-temporada frente a
  ~30 campos fijos de API-Football (long balls, through balls, big chances
  creadas/falladas, dispossessed, aerials, blocked shots, fouls drawn...).
- Los campos base (minutos, goles, asistencias, tarjetas, tiros a puerta,
  pases, rating, paradas) coinciden entre ambos proveedores dentro de un
  margen pequeño, así que la elección no sacrifica fiabilidad en lo básico.

**Consecuencias / lo que esto NO resuelve (ver `roles_fase4_mapping.md`
sección 3):**

- `lesionado` solo existe en API-Football → queda pendiente decidir si se
  ignora o se trae de forma aislada pese a que Sportmonks sea la fuente
  única de *stats*.
- `position_id` de Sportmonks es un ID numérico; hace falta su tabla de
  posiciones para tener un nombre legible.
- Dos convenciones de Sportmonks (omite valores 0; cuelga stats de equipo
  del jugador de campo) tendrán que tratarse explícitamente en el esquema
  de PostgreSQL para no contaminar los percentiles de Fase 3.

**Alcance de la validación:** la completitud de campos *estadísticos* se
midió sobre 13 jugadores de prueba (titulares habituales), NO sobre el
roster completo. La completitud de campos de *perfil* sí es sobre el roster
completo (777 filas Sportmonks). Para jugadores de rotación / poco minutaje
la completitud estadística real es desconocida y habrá que re-medirla en
Fase 2 al descargar el roster completo con estadísticas.

---

## 2026-08-30 (tarde) — Validación sobre el roster completo: 2 roles suben a "construible pleno"

**Estado:** aceptada. Amplía la entrada anterior, no la revierte.

**Qué se hizo:** se descargaron las estadísticas de temporada de **los 762
jugadores del roster de Sportmonks** (no solo los 13 de prueba), se resolvió
`position_id` / `detailed_position_id` contra la tabla de posiciones de
Sportmonks (`/core/types`, `model_type == position`) y se recalculó la
completitud con desglose **por posición** y con **19 métricas nuevas** que
antes no se habían medido. Nuevo informe: `reports/field_completeness.md`
(generado por `scripts/06_roster_completeness.py`; el de 13 jugadores pasa a
`reports/field_completeness_testplayers.md`). Mapa de posiciones:
`raw_data/sportmonks/positions_map.json`.

**Roster por posición** (con detalle Sportmonks): 190 centrocampistas,
130 centrales, 123 extremos, 113 laterales, 101 porteros, 93 delanteros
(+12 sin detalle suficiente). Con ≥600 min jugados (la población real para
percentiles): 401 jugadores — 108 centro, 76 central, 68 lateral, 61 extremo,
57 delantero, 29 portero.

**Cambios de veredicto respecto a la versión anterior de
`roles_fase4_mapping.md`:**

1. **Ball Playing CB: parcial → construible pleno.** Para centrales con
   ≥600 min, las métricas que faltaban están **al 100 %**: `long-balls`,
   `long-balls-won`, `aeriels-won` (`aeriels-won`), `clearances`,
   `blocked-shots`, además de `passes`, `accurate-passes-percentage`,
   `tackles`, `interceptions`, `duels-won` (todas 100 %). Queda una única
   salvedad menor: no hay una métrica de "pases progresivos / al último
   tercio" como tal; se proxya con balones largos + su tasa de acierto.

2. **Advanced Playmaker: parcial → construible pleno.** `big-chances-created`
   está al **96,3 % en centrocampistas y 100 % en extremos** (≥600 min),
   sumado a `key-passes` (100 %), `assists`, `successful-dribbles` (100 %).
   `through-balls` se queda en ~78-82 % (no llega al umbral de 90 %), así
   que entra como señal secundaria, no como núcleo.

3. **Poacher / Finisher: sigue parcial, pero el hueco se estrecha.**
   `big-chances-missed` está al **96,5 % en delanteros**, lo que permite un
   proxy de calidad de finalización (goles en grandes ocasiones / grandes
   ocasiones) que antes no existía. Sigue sin ser xG por localización de
   tiro, por eso no sube a pleno.

4. **Box-to-Box: sin cambios, sigue parcial.** Ninguna de las métricas
   nuevas cubre la dimensión física (distancia, sprints); ese hueco no se
   resuelve con más campos de Sportmonks.

5. **Pressing Forward: sin cambios, sigue NO construible.** Confirmado sobre
   el roster: `tackles` e `interceptions` para delanteros con ≥600 min están
   presentes, pero son totales sin zona; no hay métrica de presión /
   recuperación.

**Hallazgo sobre campos ya dados por "fiables":** el `%` de completitud
sobre el roster **entero** baja a ~77 % para los campos base (minutos,
apariciones, pases, precisión, rating). **No es una regresión:** se debe a
que ~175 de los 762 jugadores (23 %) no disputaron un solo minuto de LaLiga
2024/25 (canteranos, descartes, lesionados de larga duración) y Sportmonks
omite el detalle cuando vale 0. **Restringiendo a los 401 jugadores con
≥600 min, todos los campos base están al 100 % en todas las posiciones.**
La conclusión práctica: hay que fijar un umbral mínimo de minutos antes de
calcular percentiles (ver `roles_fase4_mapping.md` sección 3).

**Corrección a la entrada anterior:** `interceptions` se había clasificado
como "campo base que nunca se omite". No es exacto: para centrales/medios/
laterales con minutos está al ~99-100 %, pero para delanteros baja al 96 %
y para porteros al 17 % (lo omite cuando es 0). Los campos que de verdad no
se omiten nunca (100 % en todas las posiciones con ≥600 min) son:
`minutes-played`, `appearances`, `passes`, `accurate-passes-percentage`,
`rating` y `duels-won`.

---

## 2026-08-30 (cierre) — El lado L/R de la posición SÍ está en Sportmonks. Fase 4 cerrada.

**Estado:** aceptada. Cierra la Fase 4.

**Qué se comprobó:** la tabla de posiciones de Sportmonks (`/core/types`,
`model_type == position`, guardada en `raw_data/sportmonks/position_types.json`)
**sí distingue el lado**: tiene valores separados para `Left Back` (155) /
`Right Back` (154), `Left Wing` (152) / `Right Wing` (156) y
`Left Midfield` (157) / `Right Midfield` (158), frente a los "de centro"
(`Centre Back`, `Central Midfield`, `Defensive/Attacking Midfield`,
`Centre Forward`, `Secondary Striker`, `Goalkeeper`).

**Decisión:** el lado queda **RESUELTO**. `scripts/07_positions_map.py`
regenera `raw_data/sportmonks/positions_map.json` añadiendo un campo `lado`
(`izquierda` / `derecha` / `centro` / `desconocido`) **derivado únicamente
de `detailed_position_id`**, sin tocar el `bucket` de posición general que
ya existía. El lado NO se infiere del pie dominante ni de ningún otro
proxy — si en Fase 5 se quiere una lógica de "pierna cambiada", será una
decisión consciente aparte.

**Cobertura del lado en el roster (762 jugadores):**

| Bucket | centro | izquierda | derecha | desconocido |
|---|---|---|---|---|
| lateral (113) | – | 52 | 61 | – |
| extremo (123) | – | 63 | 60 | – |
| centrocampista (190) | 180 | – | – | 10 |
| central (130) | 130 | – | – | – |
| delantero (93) | 88 | – | – | 5 |
| portero (101) | 94 | – | – | 7 |

- Laterales y extremos: **el lado está para todos**.
- Centrocampistas: Sportmonks no usa `Left/Right Midfield` en esta LaLiga
  (0 jugadores) — todos son de centro. Si Fase 5 quiere "carrilero" o
  "interior de banda", el lado del centrocampista no viene de la fuente.
- **34 jugadores** (los que no tienen `detailed_position_id`) quedan con
  `lado = "desconocido"`; casi todos son de rotación / poco minutaje.

**Con esto, la Fase 4 (taxonomía de roles) se da por cerrada.** Los
pendientes que quedan abiertos son todos de Fase 1 (esquema PostgreSQL) o
posteriores — ver `roles_fase4_mapping.md` sección 3.

---

## 2026-08-31 — Nota complementaria: la consideración legal en la elección de proveedor

**Estado:** nota añadida a posteriori. **NO modifica** la entrada de
2026-08-30 ("Sportmonks es la fuente única de verdad para estadísticas de
jugador"), la complementa.

**Contexto.** Un repaso de la documentación (2026-08-31) detectó que la
entrada original solo recoge los motivos de **calidad de dato** que
confirmó el experimento de Fase 0 (`tiros_totales` diverge 30-50 %,
`precision_pases` de API-Football roto, Sportmonks más rico). Falta dejar
constancia de que la decisión de **priorizar Sportmonks desde el inicio**
también se apoyó en una consideración **legal / de licencia**, que formó
parte del razonamiento de Fase 0 pero no se anotó en su momento.

**La consideración (según el razonamiento inicial del proyecto).** Todo el
diseño asume que los datos del proveedor se **almacenan en infraestructura
propia** (PostgreSQL local hoy; lo que se despliegue en Fase 9+). Eso exige
que la licencia del proveedor lo permita:

- **Sportmonks:** se entendió, al contratar el plan, que su licencia
  autoriza **de forma explícita** el almacenamiento de los datos de la API
  en infraestructura del cliente. Es la base sobre la que se construye todo
  el esquema de `scouting-engine`.
- **API-Football (api-sports.io):** sus términos **no prohíben**
  explícitamente el almacenamiento, pero **tampoco lo autorizan por escrito**
  de forma inequívoca. Para un producto que persiste los datos, esa
  ambigüedad es un riesgo que Sportmonks no tiene.

Esta asimetría reforzó la elección de Sportmonks como fuente única, por
encima de lo que ya indicaban los datos.

**Cita literal (Sportmonks), sección "Copyright":**

> Reproduction, transferring, distribution, or storage of our services is
> strictly prohibited without the prior permission of Sportmonks. However,
> distribution, transfer, and storage of data provided by our services is
> allowed, but reselling the product is forbidden without our consent.

Y en "Terms of use":

> In principle, if you use our data to create something based on our data
> and start earning money from your creation, everything is fine.

Es decir: almacenar los datos y construir un producto derivado (incluso
comercial) está permitido; lo único prohibido sin consentimiento es
**revender los datos** y **reproducir el servicio** en sí. La asunción de
la Fase 0 se confirma.

### Actualización 2026-08-31 — términos archivados

Ver **`TOS_ARCHIVE.md`** (fecha de consulta, URLs, texto literal y
análisis). Estado de los tres pendientes:

1. **Sportmonks:** archivado y verificado verbatim. ✅
2. **API-Football / api-sports.io:** las dos URLs de términos devuelven
   **HTTP 403** a acceso automatizado (mismo bloqueo Cloudflare que en la
   Fase 0). En el archivo queda el contenido según extractos de búsqueda,
   **sin verificar verbatim**. Pendiente: abrirlas en un navegador y pegar
   el texto literal. ⚠️
3. **Repo de código público:** analizado en `TOS_ARCHIVE.md` §3 —
   **sin conflicto con Sportmonks**; **sin conflicto con API-Football para
   un repo solo-código** (no contiene datos y API-Football ni está en el
   pipeline), con un ~5 % de incertidumbre residual hasta verificar sus
   términos verbatim. La revisión de "mostrar datos en público" (Fase 10)
   sigue abierta y es un análisis aparte.

---

## 2026-09-03 — Ball Playing CB se divide en Central Constructor + Central Dominante

**Estado:** aceptada. Sustituye al rol `ball_playing_cb` de la Fase 5.

**Contexto.** El diagnóstico de la Fase 14 (ver `session_notes.md`) midió por
qué `ball_playing_cb` tenía la menor dispersión de score de todos los roles
(desv. 12.0-14.2 vs 15-24 de los demás). El hallazgo:

- **Los datos de entrada NO están comprimidos.** Cada métrica del score es
  un percentil, y `PERCENT_RANK` los hace uniformes por construcción: en el
  pool de 69 centrales de LaLiga 25/26, las 10 métricas de `ball_playing_cb`
  tienen TODAS media 50.0 y desv. 29.3.
- **La compresión nace de la combinación.** `score = Σ(pctl·peso)/Σpeso`
  sobre 10 métricas con correlación media entre pares de **+0.05** (casi
  independientes), y con pares fuertemente **anti**correlacionados:
  `accurate-passes-percentage / long-balls` **−0.51**,
  `clearances / passes` −0.42, `precisión / clearances` −0.31.
- Promediar ~10 percentiles casi independientes colapsa la desv. hacia la
  media (predicho `28.9·√(Σw²/(Σw)²)` = 11.0; observado 12.0). Las
  anticorrelaciones lo agravan: el rol mezclaba dos sub-perfiles reales que
  ningún central maximiza a la vez — el que **construye** (pase corto
  seguro, balón largo con criterio) y el que **domina el área** (duelo,
  aéreo, despeje, corte).

**Decisión: separar, no re-pesar.** Dos roles más estrechos y coherentes,
cada uno con métricas que sí correlacionan entre sí:

| rol | bucket | núcleo (peso 3) | apoyo (1.5) | contexto (0.5) | estilo de equipo |
|---|---|---|---|---|---|
| **`central_constructor`** | central | `accurate-passes-percentage`, `long-balls`, `long-balls-won` | `passes` | `interceptions` | +posesión, +precisión de pase |
| **`central_dominante`** | central | `duels-won`, `aeriels-won`, `clearances` | `blocked-shots`, `tackles` | `interceptions` | +intensidad de presión |

`central_constructor` hereda la compatibilidad de estilo del viejo rol;
`central_dominante` usa el mismo eje que Ball Winner (`press_intensity`).

**Qué se hizo con `ball_playing_cb`.** Eliminado (rol + `role_weights` +
`role_buckets` + `role_style_weights` + los 402 `player_role_scores` y sus
4020 filas de `player_role_score_breakdown`, en las 6 temporadas). No se
marcó como deprecado: `roles` no tiene columna `active`, añadirla obligaría
a filtrar en cada consulta que lista roles, y `player_role_scores` es dato
**derivado** (recomputable, DELETE-scoped + INSERT). El histórico del rol
—y este razonamiento— quedan en git y en `session_notes.md`. No hay
referencias hardcodeadas a `role_id = 4` en código; todo se resuelve por
`code` o dinámicamente desde la tabla. Migración: `db/migrate_fase15.py`.

**Resultado (validación).** Desv. estándar de los dos roles nuevos frente
al 12.0 del viejo, bucket central:

| temporada | Ball Winner (ref) | Central Constructor | Central Dominante |
|---|---|---|---|
| LaLiga 24/25 | 15.9 | 18.5 | 18.7 |
| LaLiga 25/26 | 15.2 | 17.1 | 17.6 |
| Segunda 25/26 | 15.3 | 19.1 | 18.7 |
| Premier 25/26 | 15.3 | 17.8 | 20.0 |
| Serie A 25/26 | 16.6 | 17.9 | 19.0 |
| Bundesliga 25/26 | 15.5 | 17.0 | 19.6 |

Los dos superan al viejo rol combinado y a Ball Winner: sus métricas
internas correlacionan (todo pase / todo defensa), así que la media
ponderada retiene más señal. Los centrales que antes quedaban aplastados
en 64-73 ahora se separan: Kike Salas (pésimo pasador, monstruo defensivo)
Constructor 54.9 / Dominante 89.9; Marcos Alonso y Daley Blind
(ex-laterales reconvertidos) Constructor ~85 / Dominante ~33-35; José María
Giménez (dos vías real) 70.5 / 70.9, sin destacar en ninguno.

**Actualiza** la entrada de `roles_fase4_mapping.md` sobre "Ball Playing
CB": ese rol pasa a ser estos dos.

---

## 2026-09-05 — Se reabre el entrenador (Fase 11 se revierte, no se anula) + se corrige la narrativa de `press_intensity`

**Estado:** aceptada.

### Entrenador: `active: true` ya es fiable — la Fase 11 tenía razón entonces, no ahora

La Fase 11 (2026-08-31) descartó persistir el entrenador: las fechas de
tenencia de Sportmonks estaban rotas en los límites (Osasuna sin
candidato, `end` antes del inicio de temporada). La Fase 16 repitió la
comprobación (`docs/team_analysis_sample.md`, 18 equipos de las 5 ligas) y
encontró que **eso ya no es cierto**: hay exactamente una relación
`active: true` por equipo, con fechas coherentes.

Lo que sí sigue siendo cierto: **`active` es el entrenador de HOY (temporada
2026/27), no el de la temporada que muestran las estadísticas.** De 18
equipos de la muestra, 11 tenían un entrenador distinto en 26/27
(Liverpool: Iraola vs Slot; Real Madrid: Mourinho vs Xabi Alonso; Napoli:
Allegri vs Conte…). Persistir solo `active` y llamarlo "el entrenador"
habría sido tan engañoso como no tener el dato.

**Decisión: dos vistas, nunca fusionadas.**

- `kind='current'`: `active: true` tal cual, sin `season_id` (no depende
  de qué temporada se esté mirando).
- `kind='season'`: reconstruido por solape de fechas contra
  `[seasons.start_date, seasons.end_date]` — viable ahora porque las
  fechas ya no están rotas. **9 de 18 equipos de la muestra** salen con un
  único entrenador limpio (Slot, Guardiola, Flick, Kompany, Bordalás…);
  **~4/18** con un cambio a media temporada bien identificado; **~2/18**
  sin ninguna relación que cubra la ventana (Union Berlin, Freiburg) → no
  se fuerza nada, `season` queda vacío.

**Esquema — `team_coaches`, grano por etapa.** Mismo principio que
`player_team_season`: una fila por mandato, no una columna suelta, porque
un equipo puede tener varios entrenadores en la misma temporada.
`order_in_season` numera las etapas. `kind` distingue las dos vistas en la
misma tabla (más simple que dos tablas, y `season_id` ya es NULL para
`current` así que no hay ambigüedad). Es dato **ingerido** (se recarga
desde `/teams/{id}?include=coaches.coach`, un endpoint por equipo — no
hace falta pedir por temporada), no derivado de otras tablas de la BD.

**Limitación conocida y verificada, no oculta: el filtro de "contención" puede tragarse un entrenador real.**
Para reconstruir `season` con varios candidatos solapados se descartan los
que **contienen estrictamente** el rango de otro candidato (así se
eliminan contratos de banquillo/asistente de varios años que Sportmonks
mezcla con las relaciones de primer entrenador — p. ej. "Bruno Saltor,
Chelsea, 2022-09-08→2027-06-30" solapando con el mandato real de Maresca).
Esto funciona bien en general, pero en **Tottenham** se comió también a
**Thomas Frank** (2025-07-01→2028-06-30): Sportmonks no corrigió su fecha
de fin cuando lo destituyeron en 2026, así que su rango contiene al
interinato de Tudor que le sucedió, y el filtro lo trata igual que a un
contrato fantasma. La cadena reconstruida para el Tottenham 25/26 queda
"Tudor → Saltor → De Zerbi", sin Frank al principio. No hay una señal
barata en el dato (`position_id` alterna 221/560 sin distinguir
interino/titular) que permita corregir esto sin reglas por equipo, así
que se documenta como límite conocido en vez de perseguirlo caso a caso.

### Narrativa: `press_intensity` deja de mentir sobre los equipos de posesión extrema

Diagnóstico (`docs/team_analysis_sample.md`): `press_intensity` = entradas
+ intercepciones **propias** por partido, y correlaciona fuerte y negativo
con la posesión (con el balón, el rival no lo tiene para robárselo). La
plantilla decía *"hace pocas acciones defensivas"* para el percentil bajo
de ese eje — una afirmación de pasividad defensiva que resultaba **falsa**
para equipos con pressing alto reconocido pero posesión elevada:
Liverpool (posesión p92, press p2) y Napoli (posesión p88, press p2)
salían descritos como defensivamente pasivos.

**Umbral elegido: posesión ≥ p85 suprime `press_intensity` de la frase**
(sigue en la tabla de ejes y en Tactical Fit, donde el caveat ya estaba
documentado — solo se corrige la oración). Con los datos de la muestra:
atrapa exactamente los casos con el problema (Liverpool p92, Napoli p88,
Bayern p97, City p98, Barça p98) sin tocar los casos donde el eje sigue
siendo información real — Rayo Vallecano (posesión p82, por debajo del
umbral) sigue mostrando *"hace muchas entradas e intercepciones por
partido"*, que es una lectura correcta de un equipo que presiona en bloque
medio manteniendo el balón.

**Además, las dos frases de `press_intensity` (alto y bajo) se
reformularon a lenguaje puramente factual** — "hace muchas/pocas entradas
e intercepciones por partido" en vez de "es muy activo / poco activo en
acciones defensivas" — para no editorializar sobre "actividad defensiva"
con una métrica que no distingue presión real de bloque bajo pasivo
(Getafe y Tottenham comparten percentil alto en el eje por motivos
opuestos).

Cambio en una sola función (`analysis/narrative.py::team_style_narrative`),
usada sin duplicar en las 3 vistas que muestran estilo de equipo (perfil,
Tactical Fit, fit invertido).
