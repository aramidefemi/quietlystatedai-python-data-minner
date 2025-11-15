"""LLM-based insight aggregation interface."""
from datetime import datetime
from typing import List
from db.models import ProcessedSignal, Insight
from db.mongo_client import get_db


def _generate_insight_stub(signals: List[ProcessedSignal], topic: str) -> Insight:
    """
    Generate insight from signals using stub implementation.
    TODO: Replace with LLM API call for better insight generation.
    """
    if not signals:
        raise ValueError("Cannot generate insight from empty signals list")
    
    # Aggregate signal values
    avg_value = sum(s.value_now for s in signals) / len(signals)
    entities = list(set(s.entity for s in signals))
    metrics = list(set(s.metric for s in signals))
    
    # Generate stub insight
    title = f"{topic.replace('_', ' ').title()}: {len(signals)} signals detected"
    summary = f"Found {len(signals)} signals related to {topic}. Average value change: {avg_value:.1f}%."
    implication = f"Monitor {', '.join(metrics[:3])} for {', '.join(entities[:2])}."
    
    window_start = min(s.created_at for s in signals)
    window_end = max(s.created_at for s in signals)
    
    return Insight(
        topic=topic,
        title=title,
        summary=summary,
        implication=implication,
        target_audience="ecom manager",
        signal_ids=[s.id for s in signals],
        window_start=window_start,
        window_end=window_end
    )


def generate_insights_for_window(start: datetime, end: datetime, min_signals: int = 2) -> List[Insight]:
    """
    Generate insights from signals in a time window.
    
    Groups signals by topic and generates insights for each group.
    
    Args:
        start: Window start time
        end: Window end time
        min_signals: Minimum signals required per insight
        
    Returns:
        List of Insight objects
    """
    db = get_db()
    signals_col = db.processed_signals
    
    # Fetch signals in window
    query = {
        "created_at": {"$gte": start, "$lte": end}
    }
    signal_docs = list(signals_col.find(query))
    
    if not signal_docs:
        return []
    
    # Group by topic
    from db.models import ProcessedSignal
    signals_by_topic: dict[str, List[ProcessedSignal]] = {}
    
    for doc in signal_docs:
        signal = ProcessedSignal(**doc)
        topic = signal.topic
        if topic not in signals_by_topic:
            signals_by_topic[topic] = []
        signals_by_topic[topic].append(signal)
    
    # Generate insights for each topic group
    insights = []
    for topic, signals in signals_by_topic.items():
        if len(signals) >= min_signals:
            try:
                insight = _generate_insight_stub(signals, topic)
                insights.append(insight)
            except Exception as e:
                print(f"Error generating insight for topic {topic}: {e}")
                continue
    
    return insights

