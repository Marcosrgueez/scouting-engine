"""Fase 8 - Tactical Fit Score (compatibilidad jugador-equipo).

    tactical_fit = w_role * role_score + w_style * style_compatibility

Ambos componentes en [0,100] y w_role + w_style = 1 -> score en [0,100].
Pesos por defecto 70/30, como PARAMETRO (no hardcodeado), igual que el
umbral de minutos de la Fase 3.

**No se materializa.** El role_score ya vive en player_role_scores (Fase 5)
y los percentiles de estilo en team_style_axes (analysis/team_style.py); el
producto cartesiano jugador x equipo x rol x formacion serian ~34k filas de
aritmetica trivial que quedan obsoletas al tocar el peso. Esto es una
funcion parametrizada que se ejecuta bajo demanda (patron consultado con
el usuario), con el desglose por eje para explicar cada resultado.

style_compatibility, por (jugador-rol, equipo, formacion):
    SUM(pctl_efectivo * peso) / SUM(peso)          -> [0,100]
donde pctl_efectivo = 100 - percentil  si el eje es 'negative' para el rol
                      (directitud para Deep-Lying Playmaker), si no el
                      percentil tal cual. Misma forma de combinar que el
                      Role Score de la Fase 5.

Formacion:
  - por defecto se usa el AGREGADO del equipo (team_style_axes.formation
    IS NULL).
  - by_formation=True -> una fila por el agregado Y por cada formacion del
    equipo con >= umbral de partidos (Fase 7).

Uso (CLI, para inspeccion):
    python -m analysis.tactical_fit --player "Zubimendi"
    python -m analysis.tactical_fit --player "Pedri" --role deep_lying_playmaker
    python -m analysis.tactical_fit --team "FC Barcelona" --role deep_lying_playmaker --top 10
    python -m analysis.tactical_fit --player "Rodri" --team "Getafe" --explain
    python -m analysis.tactical_fit --player "Pedri" --team "FC Barcelona" --by-formation
"""

from __future__ import annotations

import argparse
from collections import defaultdict

from sqlalchemy import text

from db.database import get_session

DEFAULT_W_ROLE = 0.70
DEFAULT_W_STYLE = 0.30

# devuelve una fila por (jugador-rol, equipo, formacion, eje de estilo):
# el ladrillo con el que se construyen score y desglose.
_CONTRIB_SQL = """
WITH rs AS (
    SELECT prs.player_id, pl.name AS player_name,
           prs.role_id, r.code AS role_code, r.label AS role_label,
           prs.position_bucket, prs.score AS role_score
    FROM player_role_scores prs
    JOIN roles r    ON r.id = prs.role_id
    JOIN players pl ON pl.id = prs.player_id
    WHERE (:player_id  IS NULL OR prs.player_id = :player_id)
      AND (:player_like IS NULL OR pl.name ILIKE :player_like)
      AND (:role_code   IS NULL OR r.code = :role_code)
      AND (:season_id   IS NULL OR prs.season_id = :season_id)
),
prof AS (
    SELECT tsa.team_id, t.name AS team_name, tsa.formation,
           tsa.style_axis, tsa.percentile, tsa.raw_value, tsa.n_matches
    FROM team_style_axes tsa
    JOIN teams t ON t.id = tsa.team_id
    WHERE (:team_id   IS NULL OR tsa.team_id = :team_id)
      AND (:team_like IS NULL OR t.name ILIKE :team_like)
      AND (:season_id IS NULL OR tsa.season_id = :season_id)
      AND (
            (:by_formation AND :formation IS NULL)
         OR (:formation IS NOT NULL AND tsa.formation = :formation)
         OR (NOT :by_formation AND :formation IS NULL AND tsa.formation IS NULL)
      )
)
SELECT rs.player_id, rs.player_name, rs.role_code, rs.role_label,
       rs.position_bucket, rs.role_score,
       prof.team_id, prof.team_name, prof.formation, prof.n_matches,
       rsw.style_axis, rsw.weight, rsw.direction,
       prof.percentile AS team_percentile, prof.raw_value AS team_raw_value,
       (CASE WHEN rsw.direction = 'negative' THEN 100 - prof.percentile
             ELSE prof.percentile END) AS effective_percentile
FROM rs
JOIN role_style_weights rsw ON rsw.role_id = rs.role_id
JOIN prof                   ON prof.style_axis = rsw.style_axis
"""


def _norm_weights(w_role, w_style):
    total = w_role + w_style
    if total <= 0:
        raise ValueError("w_role + w_style debe ser > 0")
    return w_role / total, w_style / total


def tactical_fit(session, *, player_id=None, player_like=None, team_id=None,
                 team_like=None, role_code=None, formation=None, by_formation=False,
                 w_role=DEFAULT_W_ROLE, w_style=DEFAULT_W_STYLE, season_id=None):
    """Devuelve (resultados, w_role_norm, w_style_norm).

    resultados: lista de dicts ordenada por score desc, cada uno con:
      player_id, player_name, role_code, role_label, position_bucket,
      team_id, team_name, formation, n_matches,
      role_score, style_component, score,
      breakdown: [ {style_axis, direction, team_percentile, team_raw_value,
                    effective_percentile, weight, contribution}, ... ]
    """
    wr, ws = _norm_weights(w_role, w_style)
    params = {
        "player_id": player_id, "player_like": f"%{player_like}%" if player_like else None,
        "team_id": team_id, "team_like": f"%{team_like}%" if team_like else None,
        "role_code": role_code, "formation": formation,
        "by_formation": by_formation, "season_id": season_id,
    }
    rows = session.execute(text(_CONTRIB_SQL), params).mappings().all()

    grouped = defaultdict(list)
    for r in rows:
        key = (r["player_id"], r["role_code"], r["team_id"], r["formation"])
        grouped[key].append(r)

    out = []
    for (pid, rcode, tid, form), items in grouped.items():
        first = items[0]
        wsum = sum(float(i["weight"]) for i in items)
        contribs = []
        for i in items:
            c = float(i["effective_percentile"]) * float(i["weight"])
            contribs.append({
                "style_axis": i["style_axis"],
                "direction": i["direction"],
                "team_percentile": float(i["team_percentile"]),
                "team_raw_value": float(i["team_raw_value"]),
                "effective_percentile": float(i["effective_percentile"]),
                "weight": float(i["weight"]),
                "contribution": round(c, 2),
            })
        style_component = sum(c["contribution"] for c in contribs) / wsum if wsum else 0.0
        role_score = float(first["role_score"])
        score = wr * role_score + ws * style_component
        out.append({
            "player_id": pid, "player_name": first["player_name"],
            "role_code": rcode, "role_label": first["role_label"],
            "position_bucket": first["position_bucket"],
            "team_id": tid, "team_name": first["team_name"],
            "formation": form, "n_matches": first["n_matches"],
            "role_score": round(role_score, 2),
            "style_component": round(style_component, 2),
            "score": round(score, 2),
            "breakdown": sorted(contribs, key=lambda c: -c["contribution"]),
        })

    out.sort(key=lambda r: -r["score"])
    return out, round(wr, 4), round(ws, 4)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def _print(results, wr, ws, explain=False, top=None):
    if not results:
        print("  sin resultados (¿el jugador tiene Role Score? ¿el equipo tiene estilo calculado?)")
        return
    print(f"\n  Tactical Fit  (w_role={wr}, w_style={ws})")
    shown = results[:top] if top else results
    print(f"  {'jugador':<22} {'rol':<16} {'equipo':<20} {'form':>7} "
          f"{'role':>6} {'style':>6} {'FIT':>6}")
    print("  " + "-" * 92)
    for r in shown:
        form = r["formation"] or "(agg)"
        print(f"  {r['player_name']:<22} {r['role_code']:<16} {r['team_name']:<20} "
              f"{form:>7} {r['role_score']:>6} {r['style_component']:>6} {r['score']:>6}")
        if explain:
            for b in r["breakdown"]:
                sign = "-" if b["direction"] == "negative" else "+"
                note = (f"  (dir={sign}: pctl {b['team_percentile']:.0f} -> "
                        f"efectivo {b['effective_percentile']:.0f})")
                print(f"      {b['style_axis']:<20} bruto={b['team_raw_value']:>7.2f} "
                      f"w={b['weight']}  contrib={b['contribution']:>6}{note}")
    print("  " + "-" * 92)
    print(f"  {len(results)} resultado(s)")


def main():
    ap = argparse.ArgumentParser(description="Fase 8: Tactical Fit Score (bajo demanda)")
    ap.add_argument("--player", help="nombre (ILIKE) del jugador")
    ap.add_argument("--team", help="nombre (ILIKE) del equipo")
    ap.add_argument("--role", help="code del rol (ball_winner, deep_lying_playmaker, ...)")
    ap.add_argument("--formation", help="una formacion concreta (ej '4-3-3')")
    ap.add_argument("--by-formation", action="store_true",
                    help="una fila por agregado y por cada formacion con muestra suficiente")
    ap.add_argument("--w-role", type=float, default=DEFAULT_W_ROLE)
    ap.add_argument("--w-style", type=float, default=DEFAULT_W_STYLE)
    ap.add_argument("--top", type=int, default=20)
    ap.add_argument("--explain", action="store_true", help="imprime el desglose por eje")
    args = ap.parse_args()

    session = get_session()
    try:
        results, wr, ws = tactical_fit(
            session,
            player_like=args.player, team_like=args.team, role_code=args.role,
            formation=args.formation, by_formation=args.by_formation,
            w_role=args.w_role, w_style=args.w_style,
        )
        _print(results, wr, ws, explain=args.explain, top=args.top)
    finally:
        session.close()


if __name__ == "__main__":
    main()
