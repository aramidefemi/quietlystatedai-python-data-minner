"""Bias detection for source-specific data filtering."""
import json
from typing import Dict, List, Optional
from pathlib import Path


class BiasChecker:
    """Check if data points are biased based on source rules."""
    
    def __init__(self, config_path: str = "config/bias_rules.json"):
        """Initialize with bias rules from config."""
        self.rules: Dict[str, Dict] = {}
        self._load_rules(config_path)
    
    def _load_rules(self, config_path: str) -> None:
        """Load bias rules from JSON config."""
        path = Path(config_path)
        if not path.exists():
            print(f"Warning: Bias rules file not found at {config_path}")
            return
        
        try:
            with open(path, 'r') as f:
                config = json.load(f)
                for rule in config.get("rules", []):
                    source = rule.get("source")
                    if source:
                        self.rules[source] = {
                            "reason": rule.get("reason", ""),
                            "exclude_topics": [t.lower() for t in rule.get("exclude_topics", [])],
                            "exclude_keywords": [k.lower() for k in rule.get("exclude_keywords", [])]
                        }
        except Exception as e:
            print(f"Error loading bias rules: {e}")
    
    def is_biased(
        self,
        source_origin: str,
        topic: Optional[str] = None,
        text: Optional[str] = None
    ) -> bool:
        """
        Check if a data point is biased for the given source.
        
        Args:
            source_origin: The source identifier (e.g., "recharge_blog")
            topic: The topic classification (e.g., "retention")
            text: The text content to check for biased keywords
            
        Returns:
            True if biased, False if not biased
        """
        # No rules for this source = not biased
        if source_origin not in self.rules:
            return False
        
        rule = self.rules[source_origin]
        
        # Check topic exclusion
        if topic and topic.lower() in rule["exclude_topics"]:
            return True
        
        # Check keyword exclusion in text
        if text:
            text_lower = text.lower()
            for keyword in rule["exclude_keywords"]:
                if keyword in text_lower:
                    return True
        
        return False
    
    def get_rule_info(self, source_origin: str) -> Optional[Dict]:
        """Get bias rule information for a source."""
        return self.rules.get(source_origin)
    
    def has_rules(self, source_origin: str) -> bool:
        """Check if a source has bias rules."""
        return source_origin in self.rules

