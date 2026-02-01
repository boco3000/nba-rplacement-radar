from pathlib import Path

# Repo paths (assumes notebooks live in /notebooks and code lives in /src)
REPO_ROOT = Path(__file__).resolve().parents[1]

DATA_DIR = REPO_ROOT / "data"
RAW_DIR = DATA_DIR / "raw"
REPORTS_DIR = DATA_DIR / "reports"
PROCESSED_DIR = DATA_DIR / "processed"

SEASON_DEFAULT = "2024-25"
