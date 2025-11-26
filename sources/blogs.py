"""Blog and news article ingestion module."""
import json
import ssl
from datetime import datetime
from typing import Dict, Any, Optional
import feedparser
import httpx
from bs4 import BeautifulSoup
from db.mongo_client import get_db
from db.models import RawArticle
from processing.stats_extractor import extract_stat_candidates
from processing.bias_checker import BiasChecker


# Disable SSL verification for RSS feeds (they're public)
feedparser.USER_AGENT = "QuietlyStated/1.0 (+https://github.com/quietlystated)"
ssl._create_default_https_context = ssl._create_unverified_context


def _parse_published_date(entry: Dict[str, Any]) -> datetime:
    """Parse published date from feed entry."""
    if hasattr(entry, "published_parsed") and entry.published_parsed:
        return datetime(*entry.published_parsed[:6])
    return datetime.utcnow()


def _extract_article_text(url: str, rss_content: Optional[str] = None) -> str:
    """
    Extract full article text from URL.
    Falls back to RSS content if available.
    """
    if rss_content and len(rss_content) > 500:
        return rss_content
    
    try:
        with httpx.Client(timeout=10.0, verify=False) as client:
            response = client.get(url, follow_redirects=True)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, "html.parser")
            
            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()
            
            # Try common article content selectors
            content_selectors = [
                "article",
                ".article-content",
                ".post-content",
                ".entry-content",
                "main",
                "body"
            ]
            
            text = ""
            for selector in content_selectors:
                element = soup.select_one(selector)
                if element:
                    text = element.get_text(separator=" ", strip=True)
                    if len(text) > 200:
                        break
            
            if not text or len(text) < 200:
                text = soup.get_text(separator=" ", strip=True)
            
            return text[:10000]  # Limit to 10k chars
            
    except Exception as e:
        print(f"Error fetching article content from {url}: {e}")
        return rss_content or ""


def fetch_and_store_articles(config_path: str = "config/feeds.json") -> None:
    """
    Fetch blog articles via RSS and store in MongoDB.
    
    Args:
        config_path: Path to feeds configuration file
    """
    with open(config_path, "r") as f:
        feeds = json.load(f)
    
    db = get_db()
    articles_col = db.raw_articles
    bias_checker = BiasChecker()
    
    for feed_config in feeds:
        if feed_config.get("type") != "rss":
            continue
        if feed_config.get("source", "").startswith("google_alerts_"):
            continue
        
        source_name = feed_config["source"]
        feed_url = feed_config["url"]
        
        try:
            feed = feedparser.parse(feed_url)
            total_entries = len(feed.entries)
            saved_count = 0
            skipped_count = 0
            skipped_bias = 0
            
            for entry in feed.entries:
                try:
                    published_at = _parse_published_date(entry)
                    article_url = entry.get("link", "")
                    rss_content = entry.get("content", [{}])[0].get("value", "") if entry.get("content") else entry.get("summary", "")
                    
                    text = _extract_article_text(article_url, rss_content)
                    
                    # Clean HTML from text for better stat extraction
                    from bs4 import BeautifulSoup
                    clean_text = BeautifulSoup(text, "html.parser").get_text(separator=" ", strip=True)
                    
                    # Extract data points - only save articles with quantifiable data
                    stat_candidates = extract_stat_candidates(clean_text)
                    
                    if not stat_candidates:
                        # Skip articles without any data points
                        skipped_count += 1
                        continue
                    
                    # Check for source bias
                    if bias_checker.is_biased(source_origin=source_name, text=clean_text):
                        # Skip biased articles (e.g., Recharge blog talking about subscriptions)
                        skipped_bias += 1
                        continue
                    
                    # Store up to 5 data point sentences as the "reason"
                    data_points = [candidate.sentence for candidate in stat_candidates[:5]]
                    
                    # Extract tag strings from feedparser tag dicts
                    tags = []
                    for tag in entry.get("tags", []):
                        if isinstance(tag, dict):
                            tags.append(tag.get("term", ""))
                        else:
                            tags.append(str(tag))
                    
                    article_doc = RawArticle(
                        source_origin=source_name,
                        source_url=feed_url,
                        title=entry.get("title", ""),
                        url=article_url,
                        published_at=published_at,
                        author=entry.get("author", None),
                        text=text,
                        tags_raw=tags,
                        data_points=data_points
                    )
                    
                    # Upsert by url + published_at to avoid duplicates
                    articles_col.update_one(
                        {
                            "url": article_doc.url,
                            "published_at": article_doc.published_at
                        },
                        {"$set": article_doc.model_dump(by_alias=True, exclude={"id"})},
                        upsert=True
                    )
                    saved_count += 1
                    
                except Exception as e:
                    print(f"Error processing article entry: {e}")
                    continue
            
            bias_msg = f", {skipped_bias} biased" if skipped_bias > 0 else ""
            print(f"  {source_name}: {saved_count}/{total_entries} saved ({skipped_count} no data{bias_msg})")
                    
        except Exception as e:
            print(f"Error fetching feed {source_name}: {e}")
            continue

