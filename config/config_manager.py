"""Configuration management - MongoDB backed with JSON fallback."""
import json
from datetime import datetime
from typing import Dict, Any, Optional
from pathlib import Path
from db.mongo_client import get_db


class ConfigManager:
    """Centralized configuration management."""
    
    def __init__(self):
        self.db = get_db()
        self.config_dir = Path(__file__).parent
        self._cache = {}
    
    def get_keywords_config(self) -> Dict[str, Any]:
        """Get active keywords configuration."""
        if "keywords" in self._cache:
            return self._cache["keywords"]
        
        # Try MongoDB first
        config = self.db.config_keywords.find_one({"active": True})
        
        if config:
            data = {
                "regions": config.get("regions", []),
                "timeframe": config.get("timeframe", "now 7-d"),
                "groups": config.get("groups", [])
            }
            self._cache["keywords"] = data
            return data
        
        # Fallback to JSON file
        return self._load_json_file("keywords.json")
    
    def get_feeds_config(self) -> list:
        """Get active feeds configuration."""
        if "feeds" in self._cache:
            return self._cache["feeds"]
        
        # Try MongoDB first
        config = self.db.config_feeds.find_one({"active": True})
        
        if config:
            feeds = config.get("feeds", [])
            self._cache["feeds"] = feeds
            return feeds
        
        # Fallback to JSON file
        return self._load_json_file("feeds.json")
    
    def get_topics_config(self) -> Dict[str, list]:
        """Get active topics configuration."""
        if "topics" in self._cache:
            return self._cache["topics"]
        
        # Try MongoDB first
        config = self.db.config_topics.find_one({"active": True})
        
        if config:
            topics = config.get("topics", {})
            self._cache["topics"] = topics
            return topics
        
        # Fallback to JSON file
        return self._load_json_file("topics.json")
    
    def _load_json_file(self, filename: str) -> Any:
        """Load configuration from JSON file."""
        file_path = self.config_dir / filename
        try:
            with open(file_path, "r") as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"Warning: Config file {filename} not found")
            return {} if filename == "topics.json" else []
    
    def seed_from_json(self) -> Dict[str, bool]:
        """Load all JSON configs into MongoDB."""
        results = {}
        
        # Seed keywords
        keywords_data = self._load_json_file("keywords.json")
        if keywords_data:
            self.db.config_keywords.update_one(
                {"active": True},
                {
                    "$set": {
                        "config_type": "keywords",
                        "version": 1,
                        "updated_at": datetime.utcnow(),
                        "updated_by": "seed_script",
                        "active": True,
                        "regions": keywords_data.get("regions", []),
                        "timeframe": keywords_data.get("timeframe", "now 7-d"),
                        "groups": keywords_data.get("groups", [])
                    }
                },
                upsert=True
            )
            results["keywords"] = True
        
        # Seed feeds
        feeds_data = self._load_json_file("feeds.json")
        if feeds_data:
            self.db.config_feeds.update_one(
                {"active": True},
                {
                    "$set": {
                        "config_type": "feeds",
                        "version": 1,
                        "updated_at": datetime.utcnow(),
                        "updated_by": "seed_script",
                        "active": True,
                        "feeds": feeds_data
                    }
                },
                upsert=True
            )
            results["feeds"] = True
        
        # Seed topics
        topics_data = self._load_json_file("topics.json")
        if topics_data:
            self.db.config_topics.update_one(
                {"active": True},
                {
                    "$set": {
                        "config_type": "topics",
                        "version": 1,
                        "updated_at": datetime.utcnow(),
                        "updated_by": "seed_script",
                        "active": True,
                        "topics": topics_data
                    }
                },
                upsert=True
            )
            results["topics"] = True
        
        # Clear cache
        self._cache.clear()
        
        return results
    
    def clear_cache(self):
        """Clear configuration cache."""
        self._cache.clear()
    
    def add_feed(self, source: str, url: str, feed_type: str = "rss", 
                 keyword: Optional[str] = None, enabled: bool = True) -> bool:
        """Add new feed to configuration."""
        config = self.db.config_feeds.find_one({"active": True})
        
        if not config:
            return False
        
        new_feed = {
            "source": source,
            "url": url,
            "type": feed_type,
            "enabled": enabled
        }
        
        if keyword:
            new_feed["keyword"] = keyword
        
        # Add to feeds array
        self.db.config_feeds.update_one(
            {"active": True},
            {
                "$push": {"feeds": new_feed},
                "$set": {"updated_at": datetime.utcnow()}
            }
        )
        
        self.clear_cache()
        return True
    
    def remove_feed(self, source: str) -> bool:
        """Remove feed from configuration."""
        result = self.db.config_feeds.update_one(
            {"active": True},
            {
                "$pull": {"feeds": {"source": source}},
                "$set": {"updated_at": datetime.utcnow()}
            }
        )
        
        self.clear_cache()
        return result.modified_count > 0
    
    def add_keyword_term(self, group: str, term: str) -> bool:
        """Add term to keyword group."""
        result = self.db.config_keywords.update_one(
            {"active": True, "groups.name": group},
            {
                "$addToSet": {"groups.$.terms": term},
                "$set": {"updated_at": datetime.utcnow()}
            }
        )
        
        self.clear_cache()
        return result.modified_count > 0
    
    def get_stats(self) -> Dict[str, Any]:
        """Get configuration statistics."""
        keywords_config = self.get_keywords_config()
        feeds_config = self.get_feeds_config()
        topics_config = self.get_topics_config()
        
        total_terms = sum(len(g.get("terms", [])) for g in keywords_config.get("groups", []))
        
        return {
            "keywords": {
                "regions": len(keywords_config.get("regions", [])),
                "groups": len(keywords_config.get("groups", [])),
                "total_terms": total_terms
            },
            "feeds": {
                "total": len(feeds_config),
                "enabled": len([f for f in feeds_config if f.get("enabled", True)])
            },
            "topics": {
                "total": len(topics_config)
            }
        }

