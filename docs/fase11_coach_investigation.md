> **Documento de metodología (archivado).** Registro de una investigación o decisión tomada durante el desarrollo. La validación de datos se hizo en un espacio de trabajo aparte (`data-experiment/`, no incluido en este repositorio); las rutas a `reports/`, `raw_data/` y `scripts/*.py` se refieren a ese espacio, no a este repo. Índice de docs: [`docs/README.md`](./README.md).

---

# Investigación — entrenador por equipo (Fase 11, punto 4)

Mismo criterio que la investigación de `fixtures` en la Fase 7: comprobar
contra la API real antes de comprometerse a un esquema.

- Fecha: 2026-08-31. Temporada objetivo: LaLiga 2024/25.
- Endpoint probado: `/football/teams/{id}?include=coaches.coach`.

## Qué endpoint da el dato

**`/teams/{id}?include=coaches`** es el único que devuelve entrenadores.
No hay endpoint season-scoped (`/coaches/seasons/{id}` → 404), ni
`include=coaches` en fixtures (→ 404 en este plan), ni en squads (→ 404).

Cada entrada de `coaches[]` es una relación entrenador–equipo:

```json
{ "id": 23275, "team_id": 3468, "coach_id": 455800,
  "position_id": 221, "active": false, "temporary": false,
  "start": "2021-07-01", "end": "2024-12-17" }
```

Con `include=coaches.coach` se resuelve el nombre (`coach.name`, ej.
"Carlo Ancelotti"). Nacionalidad: `coach.nationality_id` (id numérico, sin
resolver, igual que `players.nationality`).

## El problema: las fechas de tenencia no son fiables

`active` es relativo a **hoy** (2026-08-31), no a la temporada 24/25 — no
sirve para una temporada pasada.

Las fechas `start`/`end` **están sistemáticamente mal en los límites**:

| equipo | entrenador real 24/25 | lo que dice Sportmonks |
|---|---|---|
| Real Madrid | Ancelotti (toda la temporada, hasta mayo 2025) | `end: 2024-12-17` |
| Osasuna | Vicente Moreno (toda la temporada y más) | `end: 2024-08-07` — 8 días **antes** de que empezara la temporada |
| Deportivo Alavés | Luis García Plaza (1ª vuelta) → Coudet (2ª) | Luis García `end: 2024-08-07`; hueco de 4 meses hasta Coudet |

Una heurística de "coge la relación cuyo rango `[start, end]` solapa la
ventana de la temporada (2024-08-15 → 2025-05-25)" da:

- **~14/20 claramente correctos** (Simeone, Flick, Bordalás, Míchel,
  Valverde, Pellegrini, Ancelotti, Imanol, Arrasate, Íñigo Pérez…).
- **~4/20 "el entrenador de la 2ª vuelta"** en equipos que cambiaron a
  mitad de temporada (Alavés→Coudet, Valencia→Corberán, Sevilla→Pimienta,
  Valladolid→Pezzolano): defendible pero parcial.
- **Osasuna → 0 candidatos** (el `end` de Vicente Moreno cae antes del
  inicio de temporada; habría que inventar un fallback).

## Decisión: NO se persiste el entrenador. La narrativa usa solo el equipo.

El dato existe pero es **poco fiable** para fijar "el entrenador de la
temporada 24/25": fallaría de forma visible en 5-6 equipos y necesitaría
un fallback manual para Osasuna. Afirmar "Bajo Coudet, el Alavés…" cuando
Coudet solo dirigió media temporada es activamente engañoso.

Coherente con cómo el proyecto trata el dato flojo en otras fases (Pressing
Forward "no construible", xG ausente, `preferred_foot` sin dato): **no se
crea la tabla `team_coaches`**. La descripción narrativa del estilo de
equipo (punto 5) usa solo el nombre del equipo.

Si en la Fase 12 (migración a 2025/26) el dato de la temporada **en curso**
resulta fiable vía `active: true` — que sí es correcto para el presente —
se puede reconsiderar entonces, solo para la temporada actual.
