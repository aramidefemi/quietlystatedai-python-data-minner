"""Job script to extract signals from raw documents."""
import sys
from pathlib import Path
from datetime import datetime, timedelta

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from db.mongo_client import get_db
from db.models import RawArticle, RawAlert
from processing.topic_tagger import tag_topics
from processing.llm_signals import process_article, process_alert


def enrich_signals(days_back: int = 7) -> None:
    """
    Extract signals from raw articles and alerts.
    
    Args:
        days_back: Process documents from last N days
    """
    db = get_db()
    articles_col = db.raw_articles
    alerts_col = db.raw_alerts
    signals_col = db.processed_signals
    
    cutoff = datetime.utcnow() - timedelta(days=days_back)
    
    # Process articles
    articles = list(articles_col.find({
        "fetched_at": {"$gte": cutoff}
    }))
    
    for doc in articles:
        article = RawArticle(**doc)
        topics = tag_topics(article.text)
        
        # Use most common topic or default
        topic = max(topics.items(), key=lambda x: x[1])[0] if topics else "general"
        
        signals = process_article(article, topic)
        
        for signal in signals:
            # Check if signal already exists
            existing = signals_col.find_one({
                "source_id": signal.source_id,
                "context_sentence": signal.context_sentence
            })
            
            if not existing:
                signals_col.insert_one(signal.model_dump(by_alias=True))
    
    # Process alerts
    alerts = list(alerts_col.find({
        "fetched_at": {"$gte": cutoff}
    }))
    
    for doc in alerts:
        alert = RawAlert(**doc)
        text = f"{alert.title} {alert.snippet}"
        topics = tag_topics(text)
        
        topic = max(topics.items(), key=lambda x: x[1])[0] if topics else "general"
        
        signals = process_alert(alert, topic)
        
        for signal in signals:
            existing = signals_col.find_one({
                "source_id": signal.source_id,
                "context_sentence": signal.context_sentence
            })
            
            if not existing:
                signals_col.insert_one(signal.model_dump(by_alias=True))


if __name__ == "__main__":
    enrich_signals()

