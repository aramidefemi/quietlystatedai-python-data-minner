"""Analytics and reporting functions."""
from datetime import datetime, timedelta
from typing import Dict, List, Any
from collections import defaultdict
from db.mongo_client import get_db
from db.models import RawTrend, ProcessedSignal


def _calculate_avg_interest(trend: RawTrend) -> float:
    """Calculate average interest value for a trend."""
    return trend.weekly_interest


def get_top_terms(
    current_start: datetime,
    current_end: datetime,
    previous_start: datetime,
    previous_end: datetime,
    limit: int = 10
) -> Dict[str, List[Dict[str, Any]]]:
    """
    Get top terms by average interest and by growth.
    
    Returns:
        Dictionary with 'top_by_avg' and 'top_by_growth' lists
    """
    db = get_db()
    trends_col = db.raw_trends
    
    # Fetch trends in both windows
    current_trends = list(trends_col.find({
        "pulled_at": {"$gte": current_start, "$lte": current_end}
    }))
    previous_trends = list(trends_col.find({
        "pulled_at": {"$gte": previous_start, "$lte": previous_end}
    }))
    
    # Build term dictionaries
    current_by_term: Dict[str, List[float]] = defaultdict(list)
    previous_by_term: Dict[str, List[float]] = defaultdict(list)
    
    for doc in current_trends:
        trend = RawTrend(**doc)
        avg = _calculate_avg_interest(trend)
        current_by_term[trend.term].append(avg)
    
    for doc in previous_trends:
        trend = RawTrend(**doc)
        avg = _calculate_avg_interest(trend)
        previous_by_term[trend.term].append(avg)
    
    # Calculate averages and growth
    term_stats = []
    all_terms = set(current_by_term.keys()) | set(previous_by_term.keys())
    
    for term in all_terms:
        current_avg = sum(current_by_term[term]) / len(current_by_term[term]) if current_by_term[term] else 0.0
        previous_avg = sum(previous_by_term[term]) / len(previous_by_term[term]) if previous_by_term[term] else 0.0
        
        if previous_avg > 0:
            growth_pct = ((current_avg - previous_avg) / previous_avg) * 100
        else:
            growth_pct = 100.0 if current_avg > 0 else 0.0
        
        term_stats.append({
            "term": term,
            "avg_current": current_avg,
            "avg_previous": previous_avg,
            "growth_pct": growth_pct
        })
    
    # Sort and limit
    top_by_avg = sorted(term_stats, key=lambda x: x["avg_current"], reverse=True)[:limit]
    top_by_growth = sorted(term_stats, key=lambda x: x["growth_pct"], reverse=True)[:limit]
    
    return {
        "top_by_avg": top_by_avg,
        "top_by_growth": top_by_growth
    }


def get_top_topics(
    current_start: datetime,
    current_end: datetime,
    previous_start: datetime,
    previous_end: datetime,
    limit: int = 10
) -> Dict[str, List[Dict[str, Any]]]:
    """
    Get top topics by signal count and by growth.
    
    Returns:
        Dictionary with 'top_by_count' and 'top_by_growth' lists
    """
    db = get_db()
    signals_col = db.processed_signals
    
    # Fetch signals in both windows
    current_signals = list(signals_col.find({
        "created_at": {"$gte": current_start, "$lte": current_end}
    }))
    previous_signals = list(signals_col.find({
        "created_at": {"$gte": previous_start, "$lte": previous_end}
    }))
    
    # Count by topic
    current_counts: Dict[str, int] = defaultdict(int)
    previous_counts: Dict[str, int] = defaultdict(int)
    
    for doc in current_signals:
        signal = ProcessedSignal(**doc)
        current_counts[signal.topic] += 1
    
    for doc in previous_signals:
        signal = ProcessedSignal(**doc)
        previous_counts[signal.topic] += 1
    
    # Calculate growth
    topic_stats = []
    all_topics = set(current_counts.keys()) | set(previous_counts.keys())
    
    for topic in all_topics:
        current_count = current_counts[topic]
        previous_count = previous_counts[topic]
        
        if previous_count > 0:
            growth_pct = ((current_count - previous_count) / previous_count) * 100
        else:
            growth_pct = 100.0 if current_count > 0 else 0.0
        
        topic_stats.append({
            "topic": topic,
            "count_current": current_count,
            "count_previous": previous_count,
            "growth_pct": growth_pct
        })
    
    # Sort and limit
    top_by_count = sorted(topic_stats, key=lambda x: x["count_current"], reverse=True)[:limit]
    top_by_growth = sorted(topic_stats, key=lambda x: x["growth_pct"], reverse=True)[:limit]
    
    return {
        "top_by_count": top_by_count,
        "top_by_growth": top_by_growth
    }


def get_notable_stats(
    current_start: datetime,
    current_end: datetime,
    threshold: float = 5.0
) -> List[Dict[str, Any]]:
    """
    Get notable statistics with large absolute % changes.
    
    Args:
        current_start: Current window start
        current_end: Current window end
        threshold: Minimum absolute % change to include
        
    Returns:
        List of notable stat dictionaries
    """
    db = get_db()
    signals_col = db.processed_signals
    
    # Fetch recent signals
    signals = list(signals_col.find({
        "created_at": {"$gte": current_start, "$lte": current_end}
    }))
    
    notable = []
    for doc in signals:
        signal = ProcessedSignal(**doc)
        abs_value = abs(signal.value_now)
        
        if abs_value >= threshold:
            notable.append({
                "topic": signal.topic,
                "entity": signal.entity,
                "metric": signal.metric,
                "value": signal.value_now,
                "unit": signal.unit,
                "context": signal.context_sentence,
                "created_at": signal.created_at.isoformat()
            })
    
    # Sort by absolute value
    notable.sort(key=lambda x: abs(x["value"]), reverse=True)
    
    return notable[:20]  # Top 20

