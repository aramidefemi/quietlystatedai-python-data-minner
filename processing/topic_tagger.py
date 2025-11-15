"""Topic tagging from text using keyword matching."""
import json
from typing import Dict
from pathlib import Path


def load_topics(config_path: str = "config/topics.json") -> Dict[str, list]:
    """Load topic configuration."""
    with open(config_path, "r") as f:
        return json.load(f)


def tag_topics(text: str, topics_config: Dict[str, list] = None) -> Dict[str, int]:
    """
    Count topic phrase occurrences in text.
    
    Args:
        text: Input text to analyze
        topics_config: Topic configuration dict (loaded if None)
        
    Returns:
        Dictionary mapping topic names to occurrence counts
    """
    if topics_config is None:
        topics_config = load_topics()
    
    text_lower = text.lower()
    topic_counts = {}
    
    for topic, phrases in topics_config.items():
        count = 0
        for phrase in phrases:
            count += text_lower.count(phrase.lower())
        if count > 0:
            topic_counts[topic] = count
    
    return topic_counts

