from __future__ import annotations

import pandas as pd

from .data_loader import load_default_2024_25
from .metrics import composite_score, flag_low_sample

DEFAULT_STATS = ["MIN", "PTS", "REB", "AST"]

def _ensure_cols(df: pd.DataFrame, cols: list[str]) -> pd.DataFrame:
    # Some datasets may not include MIN. If missing, we can drop it safely.
    present = [c for c in cols if c in df.columns]
    return df[present].copy()

def teammate_impact_local(
    df: pd.DataFrame,
    player_name: str,
    teammate_name: str,
    min_games_without: int = 5,
    stats_cols: list[str] | None = None,
) -> pd.DataFrame:
    """
    Compute teammate deltas with vs without teammate based on shared GAME_DATE.
    """
    if stats_cols is None:
        stats_cols = DEFAULT_STATS

    df = df.copy()
    if "PLAYER_NAME" not in df.columns:
        raise ValueError("Expected canonical column PLAYER_NAME. Use data_loader normalization.")

    p_df = df[df["PLAYER_NAME"] == player_name].copy()
    t_df = df[df["PLAYER_NAME"] == teammate_name].copy()

    if p_df.empty:
        raise ValueError(f"Player not found: {player_name}")
    if t_df.empty:
        raise ValueError(f"Teammate not found: {teammate_name}")

    # Use GAME_DATE as the join key (works with your dataset); if GAME_ID exists we could upgrade later.
    teammate_dates = set(t_df["GAME_DATE"].dropna())
    with_df = p_df[p_df["GAME_DATE"].isin(teammate_dates)]
    without_df = p_df[~p_df["GAME_DATE"].isin(teammate_dates)]

    n_with = len(with_df)
    n_without = len(without_df)

    if n_without < min_games_without:
        # Return a small empty frame with metadata if sample too low
        return pd.DataFrame(
            {
                "with_teammate_avg": [],
                "without_teammate_avg": [],
                "delta_without_minus_with": [],
                "n_games_with": [],
                "n_games_without": [],
            }
        )

    # Keep only numeric columns that exist
    cols = [c for c in stats_cols if c in p_df.columns]
    with_avg = with_df[cols].mean(numeric_only=True)
    without_avg = without_df[cols].mean(numeric_only=True)

    out = pd.DataFrame({"with_teammate_avg": with_avg, "without_teammate_avg": without_avg})
    out["delta_without_minus_with"] = out["without_teammate_avg"] - out["with_teammate_avg"]
    out.loc["N_GAMES_WITH", "with_teammate_avg"] = n_with
    out.loc["N_GAMES_WITH", "without_teammate_avg"] = n_without
    return out

def build_league_radar(
    df: pd.DataFrame,
    star_min_threshold: float = 30.0,
    min_games_without: int = 10,
) -> pd.DataFrame:
    """
    For each high-minute 'star', compare each teammate’s stats with vs without the star.
    Returns long-form radar table.
    Requires TEAM_CITY and TEAM_NAME to be present (from normalization).
    """
    if "TEAM_CITY" not in df.columns or "TEAM_NAME" not in df.columns:
        raise ValueError("Dataset missing TEAM_CITY / TEAM_NAME. Update aliases or choose a dataset with team info.")

    # Find star candidates by minutes played (if MIN exists)
    if "MIN" not in df.columns:
        raise ValueError("Dataset missing MIN, cannot compute star_min_threshold-based radar.")

    star_summary = (
        df.groupby(["PLAYER_NAME", "TEAM_CITY", "TEAM_NAME"], as_index=False)["MIN"]
        .mean()
        .rename(columns={"MIN": "avg_min"})
    )

    stars = star_summary[star_summary["avg_min"] >= star_min_threshold].copy()

    rows = []
    for _, s in stars.iterrows():
        star = s["PLAYER_NAME"]
        city = s["TEAM_CITY"]
        team = s["TEAM_NAME"]

        team_df = df[(df["TEAM_CITY"] == city) & (df["TEAM_NAME"] == team)].copy()

        # Dates star played
        star_dates = set(team_df[team_df["PLAYER_NAME"] == star]["GAME_DATE"].dropna())
        if not star_dates:
            continue

        # Teammates list
        teammates = sorted(set(team_df["PLAYER_NAME"]) - {star})

        for ben in teammates:
            ben_df = team_df[team_df["PLAYER_NAME"] == ben].copy()
            if ben_df.empty:
                continue

            with_star = ben_df[ben_df["GAME_DATE"].isin(star_dates)]
            without_star = ben_df[~ben_df["GAME_DATE"].isin(star_dates)]

            n_without = len(without_star)
            if n_without < min_games_without:
                continue

            # Compute deltas
            cols = [c for c in ["MIN", "PTS", "REB", "AST"] if c in ben_df.columns]
            with_avg = with_star[cols].mean(numeric_only=True)
            without_avg = without_star[cols].mean(numeric_only=True)

            delta = (without_avg - with_avg)

            score = composite_score(
                delta_pts=float(delta.get("PTS", 0.0)),
                delta_ast=float(delta.get("AST", 0.0)),
                delta_reb=float(delta.get("REB", 0.0)),
                delta_min=float(delta.get("MIN", 0.0)),
            )

            rows.append(
                {
                    "STAR_OUT": star,
                    "TEAM_CITY": city,
                    "TEAM_NAME": team,
                    "BENEFICIARY": ben,
                    "SCORE": score,
                    "DELTA_PTS": float(delta.get("PTS", 0.0)),
                    "DELTA_AST": float(delta.get("AST", 0.0)),
                    "DELTA_REB": float(delta.get("REB", 0.0)),
                    "DELTA_MIN": float(delta.get("MIN", 0.0)),
                    "N_WITHOUT": int(n_without),
                    "LOW_SAMPLE": flag_low_sample(int(n_without), min_games=min_games_without),
                }
            )

    radar = pd.DataFrame(rows).sort_values(["SCORE"], ascending=False)
    return radar

def build_league_radar_default() -> pd.DataFrame:
    df = load_default_2024_25()
    return build_league_radar(df)
