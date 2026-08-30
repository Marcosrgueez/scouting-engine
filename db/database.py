"""Motor y sesion de SQLAlchemy.

La cadena de conexion se lee de la variable de entorno DATABASE_URL (ver
.env.example). No hay Alembic todavia: el esquema se crea con
db/create_schema.py.
"""

import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

# Carga .env desde la raiz del proyecto (scouting-engine/).
_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(_PROJECT_ROOT, ".env"))

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError(
        "Falta DATABASE_URL. Copia .env.example a .env y ajusta la cadena de conexion."
    )


class Base(DeclarativeBase):
    """Base declarativa de todos los modelos."""


# echo=False: pon SQLALCHEMY_ECHO=1 en el entorno para ver el SQL generado.
engine = create_engine(
    DATABASE_URL,
    echo=os.getenv("SQLALCHEMY_ECHO") == "1",
    future=True,
    pool_pre_ping=True,
)

SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False, future=True)


def get_session():
    """Devuelve una sesion nueva. El llamador se encarga de cerrarla."""
    return SessionLocal()
