# src/data_loader.py
from __future__ import annotations

from pathlib import Path
import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[1]  # .../nba

# ----------------------------
# Column normalization helpers
# ----------------------------

def _ensure_player_name(df: pd.DataFrame) -> pd.DataFrame:
    if "PLAYER_NAME" in df.columns:
        return df

    if {"firstName", "lastName"}.issubset(df.columns):
        df = df.copy()
        df["PLAYER_NAME"] = (
            df["firstName"].astype(str).str.strip()
            + " "
            + df["lastName"].astype(str).str.strip()
        )
        return df

    raise ValueError("Cannot construct PLAYER_NAME column")


def _rename_to_canonical(df: pd.DataFrame) -> pd.DataFrame:
    rename_map = {
        # team info
        "playerteamCity": "TEAM_CITY",
        "playerteamName": "TEAM_NAME",

        # core stats
        "numMinutes": "MIN",
        "points": "PTS",
        "reboundsTotal": "REB",
        "assists": "AST",

        # date
        "gameDateTimeEst": "GAME_DATE",
    }

    return df.rename(columns={k: v for k, v in rename_map.items() if k in df.columns})


def _ensure_game_date(df: pd.DataFrame) -> pd.DataFrame:
    if "GAME_DATE" not in df.columns:
        raise ValueError("GAME_DATE column missing")

    df = df.copy()
    df["GAME_DATE"] = pd.to_datetime(df["GAME_DATE"], errors="coerce")
    return df


def _assert_required(df: pd.DataFrame) -> None:
    required = {"PLAYER_NAME", "GAME_DATE", "PTS", "REB", "AST"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"Dataset missing required columns: {missing}")


# ----------------------------
# Public loaders
# ----------------------------

def load_boxscores_csv(path: str | Path) -> pd.DataFrame:
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Missing file: {path.resolve()}")

    df = pd.read_csv(path)
    df = _ensure_player_name(df)
    df = _rename_to_canonical(df)
    df = _ensure_game_date(df)

    _assert_required(df)
    return df


def load_default_2024_25() -> pd.DataFrame:
    raw = REPO_ROOT / "data" / "raw" / "player_stats_2024_25.csv.gz"
    if not raw.exists():
        raise FileNotFoundError(f"Could not find {raw.resolve()}")

    return load_boxscores_csv(raw)


