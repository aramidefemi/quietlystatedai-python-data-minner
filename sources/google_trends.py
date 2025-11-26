"""Google Trends ingestion module."""
import json
import time
from datetime import datetime
from typing import List, Dict, Any
from pytrends.request import TrendReq
from db.mongo_client import get_db
from db.models import RawTrend, RelatedQuery, RelatedQueries


def _chunk_terms(terms: List[str], chunk_size: int = 5) -> List[List[str]]:
    """Split terms into chunks of max size."""
    return [terms[i:i + chunk_size] for i in range(0, len(terms), chunk_size)]


def _fetch_trend_data(pytrends: TrendReq, term: str, geo: str, timeframe: str) -> Dict[str, Any]:
    """Fetch weekly total interest and related queries for a term."""
    pytrends.build_payload([term], geo=geo, timeframe=timeframe)
    
    interest_df = pytrends.interest_over_time()
    related_queries_dict = pytrends.related_queries()
    
    # Calculate weekly average interest (simplified storage)
    weekly_interest = 0.0
    if not interest_df.empty and term in interest_df.columns:
        weekly_interest = float(interest_df[term].mean())
    
    related_queries = RelatedQueries()
    if related_queries_dict and term in related_queries_dict:
        queries = related_queries_dict[term]
        if queries.get("top") is not None:
            related_queries.top = [
                RelatedQuery(query=q["query"], value=q["value"])
                for q in queries["top"].to_dict("records")
            ]
        if queries.get("rising") is not None:
            related_queries.rising = [
                RelatedQuery(
                    query=q["query"],
                    value=q["value"],
                    is_breakout=q.get("isBreakout", False)
                )
                for q in queries["rising"].to_dict("records")
            ]
    
    return {
        "weekly_interest": weekly_interest,
        "related_queries": related_queries
    }


def fetch_and_store_trends(config_path: str = "config/keywords.json") -> None:
    """
    Fetch Google Trends data and store in MongoDB.
    
    Args:
        config_path: Path to keywords configuration file
    """
    with open(config_path, "r") as f:
        config = json.load(f)
    
    db = get_db()
    trends_col = db.raw_trends
    
    pytrends = TrendReq(hl="en-GB", tz=360)
    regions = config.get("regions", ["GB"])
    timeframe = config.get("timeframe", "now 7-d")
    groups = config.get("groups", [])
    
    for group_config in groups:
        group_name = group_config["name"]
        terms = group_config["terms"]
        term_chunks = _chunk_terms(terms, chunk_size=5)
        
        for chunk in term_chunks:
            for term in chunk:
                for geo in regions:
                    try:
                        origin = f"google_trends_{geo}_{group_name}"
                        url = f"https://trends.google.com/trends/explore?geo={geo}&q={term}"
                        
                        trend_data = _fetch_trend_data(pytrends, term, geo, timeframe)
                        
                        trend_doc = RawTrend(
                            source_origin=origin,
                            source_url=url,
                            group=group_name,
                            term=term,
                            geo=geo,
                            timeframe=timeframe,
                            weekly_interest=trend_data["weekly_interest"],
                            related_queries=trend_data["related_queries"]
                        )
                        
                        # Upsert by term + geo + timeframe
                        trends_col.update_one(
                            {
                                "term": term,
                                "geo": geo,
                                "timeframe": timeframe
                            },
                            {"$set": trend_doc.model_dump(by_alias=True, exclude={"id"})},
                            upsert=True
                        )
                        
                        time.sleep(1)  # Rate limiting
                        
                    except Exception as e:
                        print(f"Error fetching trend for {term} in {geo}: {e}")
                        continue

