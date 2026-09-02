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
