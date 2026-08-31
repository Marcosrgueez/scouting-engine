# frontend — Fase 10

Interfaz React + Vite del motor de scouting. Consume la API de la Fase 9
(`../api/`).

## Arrancar

```bash
# 1. la API (desde la raíz de scouting-engine/)
python -m uvicorn api.main:app --reload        # http://127.0.0.1:8000

# 2. el frontend
cd frontend
npm install
npm run dev                                     # http://localhost:5173
```

`VITE_API_BASE` (opcional) cambia la URL de la API; por defecto
`http://127.0.0.1:8000`.

## Comandos

| | |
|---|---|
| `npm run dev` | servidor de desarrollo |
| `npm run build` | build de producción a `dist/` |
| `npm test` | smoke test de las 4 pantallas **contra la API real** (requiere uvicorn corriendo) |
| `npm run lint` | oxlint |

## Estructura

```
src/
  styles.css     sistema visual completo (tokens de color/tipo, componentes)
  api.js         cliente HTTP de la API de Fase 9
  hooks.js       useApi / useAction (fetch + estados; no React Query)
  ui.jsx         primitivas: Bar (barra 0-100), Loading, ErrorState
  format.js      posCode / sideMark / axisName
  App.jsx        shell (topbar + nav) + rutas
  pages/
    PlayerSearch.jsx   1. búsqueda con filtros
    PlayerProfile.jsx  2. ficha: foto + resumen + role fit + percentiles + similares + mejores equipos
    TeamProfile.jsx    3. estilo por formación (+ narrativa + muestra insuficiente marcada)
    TacticalFit.jsx    4. formulario -> ranking con desglose expandible
  smoke.test.jsx  vitest: renderiza cada pantalla y comprueba coherencia con Fases 5/6/8
```

## Diseño

Ver la entrada de Fase 10 en `../docs/session_notes.md` para el plan de
diseño (paleta, tipografía, principios) y la autocrítica. Resumen:

- **Concepto:** pizarra táctica de noche + mesa de análisis de
  retransmisión. Verde-pizarra desaturado como *entorno*, un único acento
  ámbar para el foco.
- **Sin librería de gráficos:** todo es la misma barra horizontal 0-100
  (`<div>` con `width %`). Un radar con 17-34 ejes es ruido; una barra
  deja *leer* cada valor. Se documenta el porqué en las notas.
- **Tablas, no rejillas de cards.** El scout compara valores por columna.
- **El desglose siempre visible o a un clic**, nunca escondido tras un
  número. Es el valor central del proyecto.
- Animación con las reglas de la guía de pulido: nada por encima de
  300ms, `ease-out` para lo que entra, curvas custom, `prefers-reduced-motion`,
  gate de hover, sin `transition: all`.
