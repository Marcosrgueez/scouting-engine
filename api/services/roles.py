"""Servicio de /roles: catálogo de los 4 roles con su definición de pesos.

Lee `roles`, `role_buckets`, `role_weights` (Player Role Score, Fase 5) y
`role_style_weights` (matriz rol->estilo del Tactical Fit, Fase 8).
"""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from db.models import Role, RoleBucket, RoleStyleWeight, RoleWeight, StatType

# orden de tiers para presentar los pesos de forma legible.
_TIER_ORDER = {"core": 0, "support": 1, "context": 2}


def list_roles(db: Session) -> dict:
    roles = db.execute(select(Role).order_by(Role.id)).scalars().all()

    buckets_by_role: dict[int, list[str]] = {}
    for rb in db.execute(select(RoleBucket)).scalars().all():
        buckets_by_role.setdefault(rb.role_id, []).append(rb.bucket)

    weights_by_role: dict[int, list] = {}
    for rw, code, label in db.execute(
        select(RoleWeight, StatType.code, StatType.label).join(
            StatType, StatType.id == RoleWeight.stat_type_id
        )
    ).all():
        weights_by_role.setdefault(rw.role_id, []).append(
            {
                "stat_type_code": code,
                "stat_type_label": label,
                "tier": rw.tier,
                "weight": float(rw.weight),
            }
        )

    style_by_role: dict[int, list] = {}
    for rsw in db.execute(select(RoleStyleWeight)).scalars().all():
        style_by_role.setdefault(rsw.role_id, []).append(
            {
                "style_axis": rsw.style_axis,
                "weight": float(rsw.weight),
                "direction": rsw.direction,
            }
        )

    items = []
    for r in roles:
        mw = sorted(
            weights_by_role.get(r.id, []),
            key=lambda w: (_TIER_ORDER.get(w["tier"], 9), -w["weight"], w["stat_type_code"]),
        )
        items.append(
            {
                "id": r.id,
                "code": r.code,
                "label": r.label,
                "buckets": sorted(buckets_by_role.get(r.id, [])),
                "metric_weights": mw,
                "style_weights": sorted(
                    style_by_role.get(r.id, []), key=lambda s: s["style_axis"]
                ),
            }
        )
    return {"items": items}
