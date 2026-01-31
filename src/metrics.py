from __future__ import annotations

import math
import pandas as pd

def _nan0(x) -> float:
    if x is None:
        return 0.0
    # handles floats + numpy floats
    try:
        if math.isnan(float(x)):
            return 0.0
    except Exception:
        return 0.0
    return float(x)

def composite_score(delta_pts: float, delta_ast: float, delta_reb: float, delta_min: float) -> float:
    """
    Simple additive score used in the radar report.
    NaNs are treated as 0 so SCORE is always defined.
    """
    return (
        _nan0(delta_pts)
        + _nan0(delta_ast)
        + _nan0(delta_reb)
        + _nan0(delta_min)
    )

def flag_low_sample(n_without: int, min_games: int = 10) -> bool:
    return n_without < min_games

def summarize_with_without(with_df: pd.DataFrame, without_df: pd.DataFrame, cols: list[str]) -> pd.DataFrame:
    """
    Returns a small table:
      with_avg, without_avg, delta (without - with)
    """
    with_avg = with_df[cols].mean(numeric_only=True)
    without_avg = without_df[cols].mean(numeric_only=True)

    out = pd.DataFrame({"with_avg": with_avg, "without_avg": without_avg})
    out["delta_without_minus_with"] = out["without_avg"] - out["with_avg"]
    return out

def composite_score(delta_pts: float, delta_ast: float, delta_reb: float, delta_min: float) -> float:
    """
    Simple additive score used in the radar report.
    Keep it intentionally simple for interpretability.
    """
    # Same weights as you used implicitly before (1x each).
    return float(delta_pts + delta_ast + delta_reb + delta_min)


def score_breakdown_row(row: pd.Series) -> dict:
    """
    Break down SCORE into its component contributions.
    Must mirror composite_score() exactly.
    """
    d_pts = float(row.get("DELTA_PTS", 0.0) or 0.0)
    d_ast = float(row.get("DELTA_AST", 0.0) or 0.0)
    d_reb = float(row.get("DELTA_REB", 0.0) or 0.0)
    d_min = float(row.get("DELTA_MIN", 0.0) or 0.0)

    # Since composite_score is simple additive:
    c_pts = d_pts
    c_ast = d_ast
    c_reb = d_reb
    c_min = d_min
    score_recomputed = c_pts + c_ast + c_reb + c_min

    return {
        "C_PTS": c_pts,
        "C_AST": c_ast,
        "C_REB": c_reb,
        "C_MIN": c_min,
        "SCORE_RECOMPUTED": score_recomputed,
    }


import pandas as pd

DELTA_COLS = ["DELTA_PTS", "DELTA_AST", "DELTA_REB", "DELTA_MIN"]

def add_score_breakdown(radar: pd.DataFrame) -> pd.DataFrame:
    """
    Adds NaN-safe SCORE and (optionally) keeps breakdown columns.

    Policy: treat missing deltas as 0 for scoring purposes.
    (Alternative policies are possible; this one makes SCORE always defined.)
    """
    out = radar.copy()

    # Ensure delta cols exist (if some pipelines omit MIN, etc.)
    for c in DELTA_COLS:
        if c not in out.columns:
            out[c] = pd.NA

    # NaN-safe score
    out["SCORE"] = out[DELTA_COLS].fillna(0).sum(axis=1)

    return out


def flag_low_sample(n_without: int, min_games: int = 10) -> bool:
    return n_without < min_games

def summarize_with_without(with_df: pd.DataFrame, without_df: pd.DataFrame, cols: list[str]) -> pd.DataFrame:
    """
    Returns a small table:
      with_avg, without_avg, delta (without - with)
    """
    with_avg = with_df[cols].mean(numeric_only=True)
    without_avg = without_df[cols].mean(numeric_only=True)
    out = pd.DataFrame(
        {"with_avg": with_avg, "without_avg": without_avg}
    )
    out["delta_without_minus_with"] = out["without_avg"] - out["with_avg"]
    return out
