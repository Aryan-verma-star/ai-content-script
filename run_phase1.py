"""Entry point for AI Content Engine Phase 1 pipeline.

Executes the scraping and synthesis pipeline to generate Trend_Brief.json
from trending content data.
"""

import logging
import sys

from phase1 import run_scraper, run_synthesizer

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)


def main() -> None:
    """Execute the full Phase 1 pipeline."""
    raw_data = run_scraper()
    run_synthesizer(raw_data)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


# ─────────────────────────────────────────────
# SETUP & RUN INSTRUCTIONS
# ─────────────────────────────────────────────
# 1. Create and activate a virtual environment:
#    python -m venv venv
#    source venv/bin/activate   # macOS/Linux
#    venv\Scripts\activate      # Windows
#
# 2. Install dependencies:
#    pip install -r requirements.txt
#
# 3. Configure environment:
#    cp .env.example .env
#    # Edit .env and fill in your API keys
#
# 4. Run the pipeline:
#    python run_phase1.py
#
# 5. Find your output at:
#    output/Trend_Brief.json
# ─────────────────────────────────────────────