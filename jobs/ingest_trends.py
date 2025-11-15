"""Job script to ingest Google Trends data."""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sources.google_trends import fetch_and_store_trends

if __name__ == "__main__":
    fetch_and_store_trends()

