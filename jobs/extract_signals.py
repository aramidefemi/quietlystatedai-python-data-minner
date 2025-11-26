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
from processing.bias_checker import BiasChecker


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
    bias_checker = BiasChecker()
    
    cutoff = datetime.utcnow() - timedelta(days=days_back)
    
    total_signals = 0
    biased_signals = 0
    saved_signals = 0
    
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
        total_signals += len(signals)
        
        for signal in signals:
            # Filter out biased signals
            if bias_checker.is_biased(
                source_origin=signal.source_origin,
                topic=signal.topic,
                text=signal.context_sentence
            ):
                biased_signals += 1
                continue
            
            # Check if signal already exists
            existing = signals_col.find_one({
                "source_origin": signal.source_origin,
                "source_url": signal.source_url,
                "context_sentence": signal.context_sentence
            })
            
            if not existing:
                signals_col.insert_one(signal.model_dump(by_alias=True))
                saved_signals += 1
    
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
        total_signals += len(signals)
        
        for signal in signals:
            # Filter out biased signals
            if bias_checker.is_biased(
                source_origin=signal.source_origin,
                topic=signal.topic,
                text=signal.context_sentence
            ):
                biased_signals += 1
                continue
            
            existing = signals_col.find_one({
                "source_origin": signal.source_origin,
                "source_url": signal.source_url,
                "context_sentence": signal.context_sentence
            })
            
            if not existing:
                signals_col.insert_one(signal.model_dump(by_alias=True))
                saved_signals += 1
    
    # Print summary
    print(f"\n📊 Signal Extraction Summary:")
    print(f"  Total signals extracted: {total_signals}")
    print(f"  Biased signals filtered: {biased_signals}")
    print(f"  New signals saved: {saved_signals}")
    if biased_signals > 0:
        bias_pct = (biased_signals / total_signals * 100) if total_signals > 0 else 0
        print(f"  Bias filter rate: {bias_pct:.1f}%")


if __name__ == "__main__":
    enrich_signals()

