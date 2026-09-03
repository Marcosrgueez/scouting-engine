> **Documento de metodología (archivado).** Registro de una investigación o decisión tomada durante el desarrollo. La validación de datos se hizo en un espacio de trabajo aparte (`data-experiment/`, no incluido en este repositorio); las rutas a `reports/`, `raw_data/` y `scripts/*.py` se refieren a ese espacio, no a este repo. Índice de docs: [`docs/README.md`](./README.md).

> **Actualización 2026-09-03 (Fase 15).** El rol **Ball Playing CB** se dividió en **Central Constructor** (pase, balón largo) y **Central Dominante** (duelo, aéreo, despeje, corte): combinaba dos facetas anticorrelacionadas y eso comprimía la dispersión del score. Ver `DECISIONS.md`, entrada del 2026-09-03. La sección 2 de abajo queda superada en ese punto.

---

# Fase 4 — Mapa rol → campos → ¿construible? (CERRADO)

Documento de decisión de la Fase 4 (taxonomía de roles). Basado en datos
**reales** del experimento de Fase 0. Fuente de stats: **Sportmonks** (ver
`DECISIONS.md`). **Fase 4 cerrada el 2026-08-30.**

Temporada validada: LaLiga 2024/25. Datos:
`reports/field_completeness.md` (roster completo) y
`reports/field_comparison.csv` (13 jugadores, Sportmonks vs API-Football).

> **Historial.** v1: veredicto sobre 13 titulares. v2 (2026-08-30 tarde):
> completitud medida sobre **los 762 jugadores del roster**, +19 métricas
> nuevas → **Ball Playing CB y Advanced Playmaker suben a "construible
> pleno"**. v3 (2026-08-30 cierre): resuelto el **lado L/R** de la posición
> (sección 3) → Fase 4 cerrada.

**Población de trabajo.** De los 762 jugadores del roster, solo **401
tienen ≥600 minutos** en LaLiga 2024/25 (los otros ~360 jugaron poco o
nada). Todo el análisis de roles se hace sobre esos 401 (o el umbral que
se fije en Fase 3). Para ellos, los campos base están al 100 %.

Roster con ≥600 min por posición: **108 centrocampistas, 76 centrales,
68 laterales, 61 extremos, 57 delanteros, 29 porteros.**

---

## 1. Campos disponibles (Sportmonks), completitud REAL sobre el roster

`% ≥600'` = jugadores con al menos 600 minutos para los que el campo
aparece. Sportmonks **omite los detalles con valor 0**: un `%` por debajo
de 100 en un contador casi siempre significa "ese jugador tuvo 0", no
"falta el dato". El `% roster` (sobre 762) es más bajo solo porque incluye
a los ~360 que apenas jugaron.

### 1a. `STAT_FIELD_MAP` (ya se usaban antes)

| Campo | code | % ≥600' | Lectura |
|---|---|---|---|
| `minutos_jugados` | `minutes-played` | 100 % | Base, nunca se omite (si jugó). |
| `apariciones` | `appearances` | 100 % | Base. |
| `pases_totales` | `passes` | 100 % | Base. |
| `precision_pases` | `accurate-passes-percentage` | 100 % | Base. `%` limpio (roto en API-Football). |
| `duelos_ganados` | `duels-won` | 100 % | Base, 100 % en TODAS las posiciones. |
| `rating_medio` | `rating` | 100 % | Media Sportmonks 0-10, opaca en su cálculo. |
| `entradas` | `tackles` | 96 % (100 % outfield) | Omite 0. Total sin zona. Portero 48 %. |
| `intercepciones` | `interceptions` | 93 % (97-100 % def/med) | Omite 0. Delantero 96 %, portero 17 %. |
| `pases_clave` | `key-passes` | 93 % (100 % med/del/ext/lat) | Omite 0. Central 89 %. |
| `tarjetas_amarillas` | `yellowcards` | 92 % | Omite 0. |
| `tiros_totales` | `shots-total` | 92 % (100 % outfield) | Omite 0. Portero 3 %. |
| `regates_exitosos` | `successful-dribbles` | 91 % (98-100 % ata/med/lat) | Omite 0. Central 82 %. |
| `tiros_a_puerta` | `shots-on-target` | 84 % | Omite 0. Med/ata 96-100 %, def 78-80 %. |
| `goles` | `goals` | 62 % | Omite 0. **Delantero 96 %, extremo 92 %, medio 67 %, central 54 %, lateral 37 %.** |
| `asistencias` | `assists` | 60 % | Omite 0. Extremo 84 %, medio 70 %, lateral 66 %, central 32 %. |
| `tarjetas_rojas` | `redcards` | 13 % | Omite 0. Inutilizable como % ; "ausente" = 0 rojas. |
| `paradas` | `saves` | 7 % (portero 100 %) | Correcto: solo porteros. |
| `goles_encajados` | `goals-conceded` | 100 % | ⚠️ **stat de EQUIPO**; fiable solo porteros. |
| `porteria_a_cero` | `cleansheets` | 99 % | ⚠️ **stat de EQUIPO**; fiable solo porteros. |

### 1b. Métricas nuevas (`STAT_FIELD_MAP_EXTRA`), medidas por primera vez

`% rel` = completitud dentro de la(s) posición(es) para la(s) que el campo
importa (≥600 min). Es el número que decide si un rol puede apoyarse en él.

| Campo | code | % ≥600' global | % en su posición relevante |
|---|---|---|---|
| `duelos_aereos_ganados` | `aeriels-won` | 99 % | **central 100 %, delantero 100 %** |
| `despejes` | `clearances` | 99.5 % | **central 100 %, lateral 100 %** |
| `balones_largos` | `long-balls` | 100 % | **central 100 %, medio 100 %, portero 100 %** |
| `balones_largos_ganados` | `long-balls-won` | 99 % | **central 100 %, medio 100 %, portero 100 %** |
| `tiros_rival_bloqueados` | `blocked-shots` | 84 % | **central 100 %, lateral 97 %** |
| `faltas_cometidas` | `fouls` | 95 % | **central 100 %, medio 100 %** |
| `faltas_recibidas` | `fouls-drawn` | 99 % | **medio 100 %, extremo 100 %, delantero 100 %** |
| `regates_intentados` | `dribble-attempts` | 93 % | **extremo 100 %, delantero 100 %, medio 100 %** |
| `regateado_(superado)` | `dribbled-past` | 97 % | **central 99 %, lateral 100 %, medio 100 %** |
| `perdidas_posesion` | `dispossessed` | 90 % | **medio 98 %, extremo 100 %, delantero 100 %** |
| `grandes_ocasiones_creadas` | `big-chances-created` | 87 % | **centrocampista 96 %, extremo 100 %** |
| `grandes_ocasiones_falladas` | `big-chances-missed` | 70 % | **delantero 96 %**, extremo 95 % |
| `centros_totales` | `total-crosses` | 87 % | **lateral 100 %, extremo 100 %** |
| `centros_precisos` | `accurate-crosses` | 72 % | **lateral 98 %, extremo 98 %** |
| `fueras_de_juego` | `offsides` | 63 % | **delantero 98 %**, extremo 98 % |
| `pases_al_hueco` | `through-balls` | 55 % | centrocampista 78 %, extremo 82 % (por debajo del umbral) |
| `al_palo` | `hit-woodwork` | 32 % | delantero 63 %, extremo 54 % (bajo; evento raro) |
| `pases_al_hueco_exitosos` | `through-balls-won` | 36 % | medio 55 %, extremo 56 % (bajo) |
| `penaltis` | `penalties` | 48 % | delantero 65 % (bajo; evento raro) |
| `tiros_propios_bloqueados` | `shots-blocked` | 90 % | delantero 98 %, extremo 100 % |

**Criterio aplicado:** un campo se considera utilizable para un rol si su
completitud es **≥90 % dentro de la posición** para la que se usa (mismo
umbral que se usó para los campos ya validados). "Omite 0" no penaliza: al
cargar en BD se imputará 0 (ver sección 3).

**Lo que Sportmonks sigue sin tener** (a nivel agregado de temporada): xG /
xA, pases progresivos / al último tercio como métrica propia, conducciones
progresivas, presiones / recuperaciones / acciones por zona, distancia
recorrida / sprints. Necesita datos de evento o tracking.

---

## 2. Rol → campos necesarios → ¿construible?

Todos los roles "construibles" lo son como **perfil de similitud al
arquetipo** (vector de métricas por 90', dentro de la posición), NO como
modelo validado contra criterio de ojeadores.

| Rol | Campos Sportmonks (todos ≥90 % en su posición salvo nota) | Veredicto | Detalle |
|---|---|---|---|
| **Ball Winner** | `entradas`, `intercepciones`, `duelos_ganados`, `tiros_rival_bloqueados`, `despejes`, `faltas_cometidas` (todos 95-100 % para central/medio/lateral) | ✅ **Construible pleno** | Núcleo defensivo completo y medido. `tarjetas_amarillas` (92 %) como proxy de intensidad. Limitación: totales sin zona, pero el rol no la exige. |
| **Deep-Lying Playmaker** | `pases_totales`, `precision_pases` (100 %), `pases_clave` (100 % medio), `balones_largos`, `balones_largos_ganados` (100 % medio); apoyo defensivo: `intercepciones` (99 %) | ✅ **Construible pleno** | Volumen + precisión + rango de pase largo, todo al 100 % para centrocampistas. Sigue sin haber "pases progresivos" como métrica propia; `balones_largos` + `pases_al_hueco` (78 %) son el proxy de verticalidad. |
| **Advanced Playmaker** | `pases_clave` (100 %), `grandes_ocasiones_creadas` (**96 % medio / 100 % extremo**), `regates_exitosos` (100 %), `asistencias` (70-84 %), `regates_intentados` (100 %) | ✅ **Construible pleno** _(era parcial)_ | `big-chances-created` cierra el hueco: mide creación de ocasión clara, no solo pase antes del tiro. `through-balls` (78-82 %) entra como señal secundaria, no núcleo. Sigue sin xA. |
| **Ball Playing CB** | `pases_totales`, `precision_pases` (100 %), `balones_largos`, `balones_largos_ganados`, `duelos_aereos_ganados`, `despejes`, `tiros_rival_bloqueados`, `entradas`, `intercepciones`, `duelos_ganados` (**todos 100 % en centrales ≥600'**) | ✅ **Construible pleno** _(era parcial)_ | Se distingue un central que construye (volumen + precisión + balón largo con acierto) de un central de corte, y ambos tienen suelo defensivo medido. Única salvedad: no hay "pase progresivo / al último tercio" como métrica; se proxya con `balones_largos_ganados` + `pases_al_hueco` (37 % en central — poco, pero es evento raro para un CB). |
| **Box-to-Box** | Ofensivo: `goles`, `asistencias`, `regates_exitosos`, `tiros_totales`, `pases_clave`, `grandes_ocasiones_creadas`. Defensivo: `entradas`, `intercepciones`, `duelos_ganados`, `faltas_cometidas`. Volumen: `minutos` | 🟡 **Parcialmente construible** _(sin cambio)_ | Todos esos campos están al 96-100 % para centrocampistas ≥600'. Se identifica bien a quien produce en ambas áreas. **Sigue faltando la dimensión física** (distancia, sprints, alta intensidad) que separa un B2B real de un mediocentro completo pero posicional. Ninguna métrica nueva la cubre. Proxy: minutos altos + volumen equilibrado en ambos extremos, declarándolo como aproximación. |
| **Poacher / Finisher** | `goles` (**96 % delantero**), `tiros_a_puerta`, `tiros_totales` (100 %), `grandes_ocasiones_falladas` (**96 % delantero**), `fueras_de_juego` (98 %), `tiros_propios_bloqueados` (98 %) | 🟡 **Parcialmente construible** _(mejora, no sube a pleno)_ | Perfil de volumen + eficiencia + posicionamiento (offsides). `big-chances-missed` permite ahora un proxy de calidad de finalización: (goles en grandes ocasiones) / (grandes ocasiones). **No es xG por localización de tiro** — no separa del todo "gran rematador" de "recibe muchas ocasiones claras". El hueco se estrecha pero no se cierra. |
| **Pressing Forward** | — | ❌ **No construible (honesto)** _(sin cambio)_ | Confirmado sobre el roster: para delanteros con ≥600', `entradas` e `intercepciones` están presentes pero son **totales sin zona de campo** y de volumen bajo. No hay métrica de presiones, contrapresiones, recuperaciones ni acciones defensivas en campo rival. Construirlo sería ruido. Requiere datos de evento. |

### Resumen

| Estado | Roles | Cambio vs. versión anterior |
|---|---|---|
| ✅ **Construible pleno (5)** | Ball Winner, Deep-Lying Playmaker, **Advanced Playmaker**, **Ball Playing CB**, (Ball Winner ya lo era) | +2 (AP y BPCB suben desde "parcial") |
| 🟡 **Parcial (2)** | Box-to-Box (sin físico), Poacher/Finisher (sin xG real) | Poacher mejora pero no sube |
| ❌ **No construible (1)** | Pressing Forward (sin presiones) | sin cambio |

**Ningún campo que dábamos por fiable resultó peor de lo esperado** para la
población con minutos: restringiendo a ≥600', todos los campos base siguen
al 100 %. El único matiz: `interceptions` no es "nunca omitido" como se
había dicho (baja al 96 % en delanteros, 17 % en porteros); para
centrales/medios/laterales sí está al ~99-100 %.

---

## 3. Pendientes explícitos

### Ya resueltos en Fase 4

- **`position_id` → nombre de posición.** `raw_data/sportmonks/positions_map.json`
  (`scripts/07_positions_map.py`) mapea los 762 jugadores a 6 buckets
  (portero / central / lateral / centrocampista / extremo / delantero) desde
  `detailed_position_id` contra `/core/types` (`model_type == position`),
  con fallback a `position_id` para 34 jugadores sin detalle. Guarda también
  `detailed_position_name` (Centre Back, Left Wing, Central Midfield...).

- **Lado izquierda / derecha / centro.** Campo `lado` en `positions_map.json`,
  derivado SOLO de `detailed_position_id` (Left/Right Back, Left/Right Wing,
  Left/Right Midfield). Cobertura: laterales y extremos tienen lado para
  todos (52 izq / 61 der laterales; 63 izq / 60 der extremos). Los
  centrocampistas salen todos "centro" (Sportmonks no usa Left/Right
  Midfield en esta LaLiga). 34 jugadores sin `detailed_position_id` quedan
  `lado = "desconocido"`. El lado NO se infiere del pie ni de otro proxy
  (ver `DECISIONS.md`). Si Fase 5 quiere lógica de "pierna cambiada" o lado
  del centrocampista, es una decisión aparte.

### Abiertos, de cara a Fase 1 (esquema PostgreSQL) y posteriores

1. **`lesionado` solo existe en API-Football.** Con Sportmonks como fuente
   única de stats: (a) ignorar el campo, (b) traerlo aislado de
   API-Football aceptando la excepción (no entra en percentiles, así que es
   defendible), o (c) buscar estado de lesión en otro `include` de
   Sportmonks (`include=...` en `/players/{id}` puede traer sidelined).
   Decisión de Fase 2.

2. **Tratamiento de las dos convenciones de Sportmonks en el esquema de
   PostgreSQL** (para no contaminar los percentiles de Fase 3):
   - **Ceros omitidos:** imputar **0 explícito** para todo campo de conteo
     cuando el jugador tiene estadística de la temporada pero el detail no
     aparece. Afecta a casi todos los campos de la sección 1 salvo los base
     y los `%`. Si se dejan como `NULL` y el percentil los ignora, se
     sobrestima a los jugadores flojos en esa métrica. Los campos base
     (`minutes-played`, `appearances`, `passes`,
     `accurate-passes-percentage`, `rating`, `duels-won`) sí pueden tratarse
     como "si falta, el jugador no jugó" → excluir del percentil.
   - **Stats de equipo colgadas del jugador:** `goals-conceded` y
     `cleansheets` → marcar en el esquema como válidas **solo para
     porteros** (columna separada o `NULL` forzado para no-porteros). Si
     entran en el percentil general de un central, lo distorsionan.

3. **Umbral mínimo de minutos.** Confirmado que hace falta: 360/762
   jugadores tienen <600 min y arrastran los `%` de completitud. Fijar el
   corte (600 tentativo; podría subirse a 900 = 10 partidos completos) por
   debajo del cual un jugador no entra en los percentiles. Decisión de
   Fase 3. La normalización por 90' es viable (minutos al 100 % para los
   que jugaron).

4. **xG / xA y datos de evento.** Box-to-Box (físico) y Poacher/Finisher
   (calidad de finalización) no son plenamente construibles con Sportmonks
   temporada; Pressing Forward no lo es en absoluto. Pendiente: decidir si
   en algún momento se incorpora una fuente de datos de evento, o si esos
   roles se marcan explícitamente como "aproximados" o "no disponibles" en
   la taxonomía.

5. **Lado del centrocampista y "pierna cambiada".** El `lado` de
   `positions_map.json` cubre laterales y extremos, pero todos los
   centrocampistas salen "centro" (Sportmonks no usa Left/Right Midfield
   aquí). Si Fase 5 quiere roles como "interior de banda" o "extremo a pie
   cambiado", hará falta o bien otra fuente para el lado del medio, o bien
   cruzar `lado` con el pie dominante — decisión consciente de Fase 5, no
   se resuelve ahora.
