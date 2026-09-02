# Capturas para el README

El README principal enlaza cuatro imágenes en esta carpeta. Para generarlas:

1. Arranca la API y el frontend:
   ```bash
   python -m uvicorn api.main:app --reload
   cd frontend && npm run dev
   ```
2. Abre `http://localhost:5173`, pon el navegador en un ancho de ~1280 px
   (el layout está pensado para ~1180 px de contenido), y toma cada captura
   como PNG. Recorta a la zona de contenido, sin la barra del navegador.
3. Guárdalas con estos nombres exactos:

| Archivo | Pantalla | Qué mostrar |
|---|---|---|
| `01-busqueda.png` | Jugadores (`/players`) | Selector de temporada en **LaLiga · 2025/2026**. Filtro `bucket = centrocampista`. La tabla densa con varias filas visibles (nombre, equipo, edad, minutos, posición). Enseña que se compara por columnas, no por cards. |
| `02-ficha.png` | Ficha (`/players/396`, Eduardo Camavinga) | Selector en **LaLiga · 2024/2025**. Cabecera con foto + el resumen narrativo ("*se perfila como Ball Winner (score 90.1)…*"). El rol **Ball Winner desplegado** mostrando el desglose como barras (entradas p100, duelos ganados p100, intercepciones p91, con `×peso`). A la derecha, algunos percentiles agrupados por categoría. |
| `03-estilo.png` | Equipo (`/teams/10`, FC Barcelona) | Selector en **LaLiga · 2024/2025**. La narrativa arriba ("*El FC Barcelona domina la posesión y elabora desde atrás, con poco balón largo*"). Las barras del agregado (posesión ~p98, directitud ~p3, presión ~p3, en gris neutro). Debajo, un par de formaciones y el bloque "muestra insuficiente" con la formación de <5 partidos. |
| `04-encaje.png` | Encaje táctico (`/fit`) | Selector en **LaLiga · 2024/2025**. Formulario: equipo = **Deportivo Alavés**, rol = **Ball Winner**, sin formación. Resultado con **Eduardo Camavinga arriba, FIT 92.3** (columnas role / style / fit). **Una fila desplegada** enseñando el desglose por eje de estilo (`press_intensity` con su percentil, marcado "(en contra)" los negativos). |

Opcional — una quinta que demuestre el multi-competición:
`05-segunda.png`, pantalla de Jugadores con el selector en **La Liga 2 ·
2025/2026** y `bucket = centrocampista`, para que se vea que el ranking es
independiente y no cruza con Primera (arriba suele salir Sergio Arribas,
Almería, Advanced Playmaker ~84).

Los PNG no se borran una vez añadidos; si rehaces una, sobrescribe el
mismo nombre.
