"""Crea el esquema en la base de datos apuntada por DATABASE_URL.

Sin Alembic todavia: esto es create_all() + poblacion de los catalogos
estaticos (positions, stat_types). create_all() crea tablas que falten
pero NO altera tablas existentes -> para cambios de esquema sobre una BD
ya poblada hay scripts de migracion manual (db/migrate_fase12b.py).

Uso:
    python -m db.create_schema            # crea lo que falte
    python -m db.create_schema --drop     # borra TODO y recrea (destructivo)
"""

import sys

from sqlalchemy import inspect

from db.database import Base, engine, get_session
from db import models  # noqa: F401  (registra los modelos en Base.metadata)
from db.seed_catalogs import seed_static_catalogs


def main():
    drop = "--drop" in sys.argv[1:]

    if drop:
        print("[create_schema] --drop: borrando todas las tablas...")
        Base.metadata.drop_all(engine)

    print("[create_schema] creando tablas...")
    Base.metadata.create_all(engine)

    tables = sorted(inspect(engine).get_table_names())
    print("[create_schema] tablas en la BD:", ", ".join(tables))

    session = get_session()
    try:
        counts = seed_static_catalogs(session)
        session.commit()
        print("[create_schema] catalogos estaticos poblados:", counts,
              "(0 = ya estaban)")
    finally:
        session.close()

    print("[create_schema] OK")


if __name__ == "__main__":
    main()
