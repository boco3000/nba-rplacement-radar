from __future__ import annotations

import sys
from pathlib import Path

# Ensure repo root is on sys.path so `import src...` works when running as a script
REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import argparse
import pandas as pd

from src.data_loader import load_default_2024_25
from src.radar import build_league_radar
from src.metrics import add_score_breakdown

def main() -> int:
    parser = argparse.ArgumentParser(description="Build league replacement radar and save CSV.")
    parser.add_argument("--star-min", type=float, default=30.0, help="Minutes threshold to define stars.")
    parser.add_argument("--min-without", type=int, default=5, help="Min games without star to include teammate.")
    parser.add_argument(
        "--out",
        type=str,
        default="data/reports/league_replacement_radar_2024_25.csv",
        help="Output CSV path (relative to repo root).",
    )
    parser.add_argument(
        "--topk-out",
        type=str,
        default="data/reports/top_replacements_by_star_2024_25.csv",
        help="Optional top-K per star output CSV path.",
    )
    parser.add_argument("--topk", type=int, default=5, help="Top K replacements per star to export.")
    parser.add_argument("--include-low-sample", action="store_true", help="Include LOW_SAMPLE rows in topK output.")
    args = parser.parse_args()

    # Anchor repo root as parent of /scripts
    repo_root = Path(__file__).resolve().parents[1]

    # Load
    df = load_default_2024_25()

    # Build
    radar = build_league_radar(df, star_min_threshold=args.star_min, min_games_without=args.min_without)
    radar = add_score_breakdown(radar)

    # Validate (hard fail if something is off)
    required = ["STAR_OUT", "TEAM_CITY", "TEAM_NAME", "BENEFICIARY", "SCORE", "N_WITHOUT", "LOW_SAMPLE"]
    missing = [c for c in required if c not in radar.columns]
    if missing:
        raise AssertionError(f"Radar missing columns: {missing}")
    if not radar["SCORE"].notna().all():
        n_bad = int(radar["SCORE"].isna().sum())
        raise AssertionError(f"Radar SCORE contains NaNs (count={n_bad})")

    # Save radar
    out_path = (repo_root / args.out).resolve()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    radar.to_csv(out_path, index=False)

    # Read-back check
    check = pd.read_csv(out_path)
    if len(check) != len(radar):
        raise AssertionError(f"Readback rowcount mismatch: {len(check)} vs {len(radar)}")
    if not check["SCORE"].notna().all():
        raise AssertionError("Readback SCORE contains NaNs")

    # Top-K per star export (your Day 13 artifact)
    rep = radar.copy()
    if not args.include_low_sample:
        rep = rep[~rep["LOW_SAMPLE"]].copy()

    rep["RANK"] = (
        rep.groupby("STAR_OUT")["SCORE"]
        .rank(method="first", ascending=False)
        .astype(int)
    )
    rep_top = rep[rep["RANK"] <= args.topk].copy()
    rep_top = rep_top.sort_values(["STAR_OUT", "RANK"])

    topk_path = (repo_root / args.topk_out).resolve()
    topk_path.parent.mkdir(parents=True, exist_ok=True)
    rep_top.to_csv(topk_path, index=False)

    print("OK")
    print("Radar saved:", out_path)
    print("TopK saved:", topk_path)
    print("Radar shape:", radar.shape)
    print("TopK shape:", rep_top.shape)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
