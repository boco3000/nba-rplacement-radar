# NBA Replacement Radar (2024–25)

A data project that estimates which players benefit most when a high-minute teammate is out (a simple “replacement radar”).
Built from local box score data (no live API dependency due to unstableness).

## What it does
- Computes “with vs without” splits for teammates
- Ranks likely beneficiaries when a star is absent
- Exports CSV + HTML reports

## Repo structure
- `notebooks/` — analysis and development notebooks
- `data/reports/` — generated outputs (CSV/HTML)
- `data/raw/` — ignored (source datasets not committed)

## How to run
1. Create/activate a Python environment
2. Install deps:
   ```bash
   pip install pandas numpy matplotlib
