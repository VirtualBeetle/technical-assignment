"""
Loads the manually-verified, structured financial dataset that powers the
running application (data/senus_financials.json at the repo root).

Why a curated JSON file is the source of truth for the live app, rather than
extract_pdfs.py's regex/OCR output directly:

  Two of the four source filings (the ADF Farm Solutions annual accounts and
  the Senus Limited balance sheet as at 8 Dec 2025) are scanned/image-only
  PDFs with no text layer, so extraction requires OCR. OCR + regex parsing of
  accounting tables is good but imperfect (see app/ingestion/extract_pdfs.py
  and its docstring for the specific ambiguities, e.g. note-reference numbers
  sitting between a line label and its values). Rather than silently trusting
  noisy OCR output in a financial reporting tool, this project follows a
  "trust but verify" pipeline:

    1. extract_pdfs.py runs real OCR + regex extraction against the raw PDFs
       and produces a field-by-field comparison against this gold dataset
       (see `python -c "from app.ingestion.extract_pdfs import run; run()"`).
    2. Every figure in senus_financials.json was cross-checked by hand against
       the source PDF it cites in its "provenance" section.
    3. The application (this file) loads the verified dataset, so the board
       report a CEO sees is always built from validated numbers - exactly the
       "AI extracts, a human/process validates before it reaches decision-makers"
       pattern you'd want in a real financial product.
"""
import json
import os
from pathlib import Path
from typing import Any

# repo_root/data/senus_financials.json (local dev). In Docker the backend
# code is copied to /app directly (one level shallower than the local
# "repo_root/backend/app/..." layout), so relying on parents[3] there would
# resolve to the wrong directory - docker-compose.yml sets DATA_DIR=/app/data
# explicitly to sidestep that, matching its `./data:/app/data` volume mount.
_env_data_dir = os.environ.get("DATA_DIR")
if _env_data_dir:
    DATA_DIR = Path(_env_data_dir)
else:
    DATA_DIR = Path(__file__).resolve().parents[3] / "data"

GOLD_DATASET_PATH = DATA_DIR / "senus_financials.json"


def load_gold_dataset() -> dict[str, Any]:
    with open(GOLD_DATASET_PATH, "r", encoding="utf-8") as f:
        return json.load(f)
