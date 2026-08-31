"""Fase 9 — API FastAPI del motor de scouting.

Expone el núcleo analítico de las Fases 1-8 por HTTP. NO reimplementa nada
de `analysis/`: los routers -> servicios -> (módulos de analysis / consultas
a las tablas que esos módulos poblaron).

- Sin autenticación (decisión de Fase 9).
- Documentación automática en /docs (Swagger) y /redoc.
- CORS abierto (`*`): la Fase 10 (frontend) es un cliente aparte y no hay
  auth ni cookies que proteger.

Arranque local:
    uvicorn api.main:app --reload
    -> http://127.0.0.1:8000/docs
"""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routers import players, roles, scouting, teams

app = FastAPI(
    title="Scouting Engine API",
    version="0.9.0",
    description=(
        "Motor de scouting de fútbol sobre LaLiga 2024/25 (datos de Sportmonks). "
        "Percentiles por posición, Player Role Score, Similarity Engine, Team Style "
        "Profile y Tactical Fit Score. Fase 9: solo backend."
    ),
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(players.router)
app.include_router(teams.router)
app.include_router(roles.router)
app.include_router(scouting.router)


@app.get("/", tags=["meta"], summary="Índice de la API")
def root():
    return {
        "name": "Scouting Engine API",
        "version": app.version,
        "docs": "/docs",
        "openapi": "/openapi.json",
        "endpoints": [
            "GET  /players",
            "GET  /players/{id}",
            "GET  /players/{id}/similar",
            "GET  /players/{id}/roles",
            "GET  /teams",
            "GET  /teams/{id}/style",
            "GET  /roles",
            "POST /scouting/tactical-fit",
        ],
    }


@app.get("/health", tags=["meta"], summary="Chequeo de vida + conexión a BD")
def health():
    from sqlalchemy import text

    from db.database import get_session

    db = get_session()
    try:
        db.execute(text("SELECT 1"))
        return {"status": "ok", "database": "ok"}
    except Exception as exc:  # noqa: BLE001
        return {"status": "degraded", "database": f"error: {exc}"}
    finally:
        db.close()
