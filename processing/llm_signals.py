"""LLM-based signal extraction interface."""
from typing import List, Optional, Any, Tuple
from db.models import RawArticle, RawAlert, ProcessedSignal
from processing.stats_extractor import extract_stat_candidates, StatCandidate


def _parse_percentage(value_str: str) -> Optional[float]:
    """Parse percentage string to float."""
    try:
        cleaned = value_str.replace("%", "").strip()
        return float(cleaned)
    except (ValueError, AttributeError):
        return None


def _extract_entity_and_metric(sentence: str) -> Tuple[str, str]:
    """
    Simple heuristic to extract entity and metric from sentence.
    TODO: Replace with LLM call for better extraction.
    """
    # Basic heuristics - will be replaced with LLM
    words = sentence.lower().split()
    
    # Look for common metric keywords
    metric_keywords = ["consumption", "sales", "revenue", "growth", "decline", "increase", "decrease"]
    metric = "unknown"
    for keyword in metric_keywords:
        if keyword in sentence.lower():
            metric = keyword
            break
    
    # Entity is harder - for now use first few words before metric
    entity = "unknown entity"
    if metric != "unknown":
        metric_idx = sentence.lower().find(metric)
        if metric_idx > 0:
            entity = sentence[:metric_idx].strip()[:50]
    
    return entity, metric


def extract_structured_signals(text: str, source_id: Any, origin_type: str, topic: str) -> List[ProcessedSignal]:
    """
    Extract structured signals from text.
    
    Currently uses regex-based extraction. TODO: Replace with LLM API call.
    
    Args:
        text: Input text
        source_id: Source document ID
        origin_type: "article" or "alert"
        topic: Topic classification
        
    Returns:
        List of ProcessedSignal objects
    """
    candidates = extract_stat_candidates(text)
    signals = []
    
    for candidate in candidates:
        value = _parse_percentage(candidate.raw_value_str)
        if value is None:
            continue
        
        entity, metric = _extract_entity_and_metric(candidate.sentence)
        
        signal = ProcessedSignal(
            source_id=source_id,
            origin_type=origin_type,
            topic=topic,
            entity=entity,
            metric=metric,
            value_now=value,
            unit="percent",
            time_ref="recent",
            context_sentence=candidate.sentence,
            model_used="stub",
            confidence=0.5
        )
        signals.append(signal)
    
    return signals


def process_article(article: RawArticle, topic: str) -> List[ProcessedSignal]:
    """Process a raw article into signals."""
    return extract_structured_signals(
        article.text,
        article.id,
        "article",
        topic
    )


def process_alert(alert: RawAlert, topic: str) -> List[ProcessedSignal]:
    """Process a raw alert into signals."""
    text = f"{alert.title} {alert.snippet}"
    return extract_structured_signals(
        text,
        alert.id,
        "alert",
        topic
    )

