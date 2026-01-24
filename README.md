# NBA Replacement Radar (2024–25)

A data project that estimates which players benefit most when a high-minute teammate is out (a simple “replacement radar”).
Built from local box score data (no live API dependency due to unstableness).

## What it does
- Computes “with vs without” splits for teammates
- Ranks likely beneficiaries when a star is absent
- Exports CSV + HTML reports

- ## Approach

- Uses per-game box score data for the 2024–25 NBA season
- Identifies games where a high-usage player (“star”) did not play
- Compares teammate performance with vs without the star
- Computes deltas across minutes, points, rebounds, and assists
- Applies minimum game thresholds to reduce noise

- ## Example Insights

- Some guards show meaningful increases in assists and minutes when a primary ball-handler is out, but these effects often disappear under stricter sample thresholds.
- Apparent “replacement spikes” for end-of-bench players are common in small samples, reinforcing the importance of minimum game filters.

- ## Limitations

- Player absence is inferred from game participation only (no injury timing granularity)
- Does not account for opponent strength or lineup combinations
- Sample sizes vary significantly by team and player

- ### Data

Raw box score data is not included in this repository.

To run the analysis:
- Place per-game NBA box score data for the 2024–25 season into `data/raw/`
- Data must include player name, team, game ID/date, minutes, points, rebounds, and assists

All analysis notebooks read from this directory.

## Repo structure
- `notebooks/` — analysis and development notebooks
- `data/reports/` — generated outputs (CSV/HTML)
- `data/raw/` — ignored (source datasets not committed)

## How to run
1. Create/activate a Python environment
2. Install deps:
   ```bash
   pip install pandas numpy matplotlib
