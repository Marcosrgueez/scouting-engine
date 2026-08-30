"""Mapeo de valores de Sportmonks al esquema interno.

Compartido por el smoke test (Fase 1) y el ETL masivo (Fase 2).
"""

from __future__ import annotations

from typing import Optional

# Campos que Sportmonks NUNCA omite si el jugador jugo. Si faltan en una
# etapa, NO se imputan a 0 (ver data-experiment/docs/DECISIONS.md): que
# falten significa que el jugador no jugo en esa etapa.
BASE_CODES = frozenset({
    "minutes-played", "appearances", "passes",
    "accurate-passes-percentage", "rating", "duels-won",
})


def unwrap(value):
    """El `value` de un detail de Sportmonks es siempre un dict.

    {'total': N}              -> contadores
    {'average': N, ...}       -> rating, average-points-per-game
    {'in': N, 'out': N}       -> substitutions (sin escalar util -> None)
    {'crosses_blocked': N}    -> clave unica rara
    """
    if not isinstance(value, dict):
        return value
    if "total" in value:
        return value["total"]
    if "average" in value:
        return value["average"]
    if len(value) == 1:
        only = next(iter(value.values()))
        return only if isinstance(only, (int, float)) else None
    return None


def to_number(value) -> Optional[float]:
    if isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        try:
            return float(value.strip())
        except ValueError:
            return None
    return None


def details_to_code_value(details) -> dict:
    """Lista de StatDetail (o dicts crudos) -> {code: valor_numerico_o_None}."""
    out = {}
    for det in details:
        if hasattr(det, "code"):
            code = det.code
            raw_value = det.value
        else:  # dict crudo
            code = (det.get("type") or {}).get("code")
            raw_value = det.get("value")
        if not code:
            continue
        out[code] = to_number(unwrap(raw_value))
    return out


def build_stat_rows(code_value: dict, stat_types, is_goalkeeper: bool):
    """Genera las filas de player_statistics para UNA etapa.

    stat_types: iterable de objetos con .id, .code, .valid_for.
    Devuelve lista de dicts {stat_type_id, value, is_imputed_zero}.

    Reglas:
      - stat_type goalkeeper_only y el jugador NO es portero -> se omite.
      - code presente y numerico -> valor real, is_imputed_zero=False.
      - code presente pero no numerico -> se omite (raro).
      - code ausente y es "base" -> se omite (el jugador no jugo asi).
      - code ausente y NO es base -> se imputa 0, is_imputed_zero=True.
    """
    rows = []
    for st in stat_types:
        if st.valid_for == "goalkeeper_only" and not is_goalkeeper:
            continue
        if st.code in code_value:
            number = code_value[st.code]
            if number is None:
                continue
            rows.append({"stat_type_id": st.id, "value": number, "is_imputed_zero": False})
        else:
            if st.code in BASE_CODES:
                continue
            rows.append({"stat_type_id": st.id, "value": 0, "is_imputed_zero": True})
    return rows
