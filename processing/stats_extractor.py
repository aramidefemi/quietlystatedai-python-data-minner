"""Statistics extraction from text using regex patterns."""
import re
from dataclasses import dataclass
from typing import List


@dataclass
class StatCandidate:
    """Candidate statistic found in text."""
    sentence: str
    raw_value_str: str


def _extract_sentence_around_match(text: str, match: re.Match, context_chars: int = 100) -> str:
    """Extract sentence containing the match."""
    start = max(0, match.start() - context_chars)
    end = min(len(text), match.end() + context_chars)
    
    # Try to find sentence boundaries
    sentence_start = text.rfind(".", start, match.start())
    if sentence_start == -1:
        sentence_start = start
    else:
        sentence_start += 1
    
    sentence_end = text.find(".", match.end(), end)
    if sentence_end == -1:
        sentence_end = end
    
    sentence = text[sentence_start:sentence_end].strip()
    return sentence


def extract_stat_candidates(text: str) -> List[StatCandidate]:
    """
    Extract candidate statistics from text using regex patterns.
    
    Patterns:
    - Percentages: -?\d+(\.\d+)?%
    - "from X to Y" patterns
    - "up/down by X%" patterns
    
    Args:
        text: Input text to analyze
        
    Returns:
        List of StatCandidate objects
    """
    candidates = []
    
    # Pattern 1: Percentages
    percent_pattern = r'-?\d+(?:\.\d+)?%'
    for match in re.finditer(percent_pattern, text):
        sentence = _extract_sentence_around_match(text, match)
        candidates.append(StatCandidate(
            sentence=sentence,
            raw_value_str=match.group()
        ))
    
    # Pattern 2: "from X to Y" or "X to Y"
    from_to_pattern = r'(?:from\s+)?(-?\d+(?:\.\d+)?(?:%|percent|points)?)\s+to\s+(-?\d+(?:\.\d+)?(?:%|percent|points)?)'
    for match in re.finditer(from_to_pattern, text, re.IGNORECASE):
        sentence = _extract_sentence_around_match(text, match)
        value_str = f"{match.group(1)} to {match.group(2)}"
        candidates.append(StatCandidate(
            sentence=sentence,
            raw_value_str=value_str
        ))
    
    # Pattern 3: "up/down by X%" or "increased/decreased by X%"
    change_pattern = r'(?:up|down|increased?|decreased?|rose|fell|dropped?|grew)\s+(?:by\s+)?(-?\d+(?:\.\d+)?(?:%|percent|points)?)'
    for match in re.finditer(change_pattern, text, re.IGNORECASE):
        sentence = _extract_sentence_around_match(text, match)
        candidates.append(StatCandidate(
            sentence=sentence,
            raw_value_str=match.group(1)
        ))
    
    return candidates

