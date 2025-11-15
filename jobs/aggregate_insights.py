"""Job script to aggregate insights from signals."""
import sys
from pathlib import Path
from datetime import datetime, timedelta

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from db.mongo_client import get_db
from processing.llm_insights import generate_insights_for_window


def aggregate_insights(days: int = 7) -> None:
    """
    Generate insights for a time window.
    
    Args:
        days: Number of days to look back
    """
    db = get_db()
    insights_col = db.insights
    
    end = datetime.utcnow()
    start = end - timedelta(days=days)
    
    insights = generate_insights_for_window(start, end)
    
    for insight in insights:
        # Check if insight already exists
        existing = insights_col.find_one({
            "topic": insight.topic,
            "window_start": insight.window_start,
            "window_end": insight.window_end
        })
        
        if not existing:
            insights_col.insert_one(insight.model_dump(by_alias=True))


if __name__ == "__main__":
    aggregate_insights()

