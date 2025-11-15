"""Google Alerts ingestion module (RSS-based)."""
import json
from datetime import datetime
from typing import Dict, Any
from bson import ObjectId
import feedparser
from pymongo.collection import Collection
from db.mongo_client import get_db
from db.models import Source, RawAlert


def _get_or_create_source(origin: str, url: str, sources_col: Collection) -> ObjectId:
    """Get existing source or create new one."""
    source = sources_col.find_one({"origin": origin, "url": url})
    if source:
        return source["_id"]
    
    new_source = Source(
        type="alert",
        origin=origin,
        url=url
    )
    result = sources_col.insert_one(new_source.model_dump(by_alias=True))
    return result.inserted_id


def _parse_published_date(entry: Dict[str, Any]) -> datetime:
    """Parse published date from feed entry."""
    if hasattr(entry, "published_parsed") and entry.published_parsed:
        return datetime(*entry.published_parsed[:6])
    return datetime.utcnow()


def fetch_and_store_alerts(config_path: str = "config/feeds.json") -> None:
    """
    Fetch Google Alerts via RSS and store in MongoDB.
    
    Args:
        config_path: Path to feeds configuration file
    """
    with open(config_path, "r") as f:
        feeds = json.load(f)
    
    db = get_db()
    sources_col = db.sources
    alerts_col = db.raw_alerts
    
    for feed_config in feeds:
        if feed_config.get("type") != "rss":
            continue
        if not feed_config.get("source", "").startswith("google_alerts_"):
            continue
        
        source_name = feed_config["source"]
        feed_url = feed_config["url"]
        keyword = feed_config.get("keyword", "")
        
        try:
            feed = feedparser.parse(feed_url)
            
            source_id = _get_or_create_source(source_name, feed_url, sources_col)
            
            for entry in feed.entries:
                try:
                    published_at = _parse_published_date(entry)
                    
                    alert_doc = RawAlert(
                        source_id=source_id,
                        keyword=keyword,
                        title=entry.get("title", ""),
                        snippet=entry.get("summary", ""),
                        url=entry.get("link", ""),
                        published_at=published_at
                    )
                    
                    # Upsert by url + published_at to avoid duplicates
                    alerts_col.update_one(
                        {
                            "url": alert_doc.url,
                            "published_at": alert_doc.published_at
                        },
                        {"$set": alert_doc.model_dump(by_alias=True, exclude={"id"})},
                        upsert=True
                    )
                    
                except Exception as e:
                    print(f"Error processing alert entry: {e}")
                    continue
                    
        except Exception as e:
            print(f"Error fetching feed {source_name}: {e}")
            continue

