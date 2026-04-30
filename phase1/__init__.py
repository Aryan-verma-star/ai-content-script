"""Phase 1 package for AI Content Automation Engine.

Exposes the run_scraper and run_synthesizer functions for the pipeline.
"""

from phase1.scraper import run_scraper
from phase1.synthesizer import run_synthesizer

__all__ = ["run_scraper", "run_synthesizer"]