"""Fase 15 - migración: dividir Ball Playing CB en dos roles.

El diagnóstico de la Fase 14 (ver docs/DECISIONS.md) mostró que
`ball_playing_cb` combina dos facetas anticorrelacionadas (pase corto vs
despeje/duelo), lo que comprimía la dispersión del score. Se sustituye por:

  central_constructor  — pase, balón largo, volumen
  central_dominante    — duelos, aéreos, despejes, corte

Idempotente. NO recalcula scores (eso es `analysis.role_scores`); solo
toca el catálogo y borra los scores del rol viejo.

Uso:
    python -m db.migrate_fase15
    python -m db.migrate_fase15 --dry-run
"""

from __future__ import annotations

import sys

from sqlalchemy import text

from db.database import engine

OLD_CODE = "ball_playing_cb"

TIER_WEIGHT = {"core": 3.0, "support": 1.5, "context": 0.5}

# (code, label, [buckets], {tier: [stat codes]}, [(style_axis, direction), ...])
NEW_ROLES = [
    (
        "central_constructor", "Central Constructor", ["central"],
        {
            "core":    ["accurate-passes-percentage", "long-balls", "long-balls-won"],
            "support": ["passes"],
            "context": ["interceptions"],
        },
        [("possession", "positive"), ("pass_accuracy", "positive")],
    ),
    (
        "central_dominante", "Central Dominante", ["central"],
        {
            "core":    ["duels-won", "aeriels-won", "clearances"],
            "support": ["blocked-shots", "tackles"],
            "context": ["interceptions"],
        },
        [("press_intensity", "positive")],
    ),
]


def run(dry_run=False):
    steps: list[str] = []
    conn = engine.connect()
    trans = conn.begin()
    try:
        old_id = conn.execute(
            text("SELECT id FROM roles WHERE code = :c"), {"c": OLD_CODE}
        ).scalar()

        if old_id is not None:
            n_scores = conn.execute(
                text("SELECT count(*) FROM player_role_scores WHERE role_id = :r"), {"r": old_id}
            ).scalar()
            steps.append(f"DELETE {n_scores} player_role_scores de {OLD_CODE} (+ breakdown por cascade)")
            steps.append(f"DELETE role {OLD_CODE} (+ role_weights / role_buckets / role_style_weights por cascade)")
            if not dry_run:
                conn.execute(text("DELETE FROM player_role_scores WHERE role_id = :r"), {"r": old_id})
                conn.execute(text("DELETE FROM roles WHERE id = :r"), {"r": old_id})

        stat_id = dict(conn.execute(text("SELECT code, id FROM stat_types")).all())

        for code, label, buckets, tiers, styles in NEW_ROLES:
            exists = conn.execute(text("SELECT id FROM roles WHERE code = :c"), {"c": code}).scalar()
            if exists is not None:
                steps.append(f"role {code}: ya existe (id {exists}), se salta")
                continue
            steps.append(f"INSERT role {code} ({label}) + {sum(len(v) for v in tiers.values())} pesos "
                         f"+ {len(buckets)} bucket(s) + {len(styles)} ejes de estilo")
            if dry_run:
                continue
            rid = conn.execute(
                text("INSERT INTO roles (code, label) VALUES (:c, :l) RETURNING id"),
                {"c": code, "l": label},
            ).scalar()
            for b in buckets:
                conn.execute(
                    text("INSERT INTO role_buckets (role_id, bucket) VALUES (:r, :b)"),
                    {"r": rid, "b": b},
                )
            for tier, codes in tiers.items():
                for sc in codes:
                    conn.execute(
                        text("INSERT INTO role_weights (role_id, stat_type_id, weight, tier) "
                             "VALUES (:r, :s, :w, :t)"),
                        {"r": rid, "s": stat_id[sc], "w": TIER_WEIGHT[tier], "t": tier},
                    )
            for axis, direction in styles:
                conn.execute(
                    text("INSERT INTO role_style_weights (role_id, style_axis, weight, direction) "
                         "VALUES (:r, :a, 1.0, :d)"),
                    {"r": rid, "a": axis, "d": direction},
                )

        if dry_run:
            trans.rollback()
        else:
            trans.commit()
    except Exception:
        trans.rollback()
        raise
    finally:
        conn.close()

    print("=" * 60)
    print("  migración Fase 15 -", "DRY-RUN (rollback)" if dry_run else "APLICADA")
    print("=" * 60)
    for s in steps or ["  nada que hacer (ya migrado)"]:
        print(f"  - {s}")
    print("=" * 60)
    if not dry_run and steps:
        print("  AHORA: recalcular scores ->")
        print("    for s in 1 3 7 9 11 13; do python -m analysis.role_scores --season-id $s; done")


if __name__ == "__main__":
    run(dry_run="--dry-run" in sys.argv[1:])
