"""Sources API router."""
from typing import Optional, List
from fastapi import APIRouter, Query, HTTPException
from pymongo.collection import Collection
from bson import ObjectId
from db.mongo_client import get_db
from db.models import RawArticle, RawAlert, RawTrend, ProcessedSignal, Insight

router = APIRouter()


@router.get("/articles/{article_id}")
def get_article(article_id: str) -> dict:
    """
    Get article details and associated signals/insights.
    
    Args:
        article_id: Article document ID
    """
    db = get_db()
    articles_col: Collection = db.raw_articles
    signals_col: Collection = db.processed_signals
    insights_col: Collection = db.insights
    
    try:
        doc = articles_col.find_one({"_id": ObjectId(article_id)})
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid article ID")
    
    if not doc:
        raise HTTPException(status_code=404, detail="Article not found")
    
    article = RawArticle(**doc)
    result = article.model_dump(by_alias=True, mode="json")
    
    # Get associated signals
    signals = list(signals_col.find({
        "source_origin": article.source_origin,
        "source_url": article.source_url
    }))
    result["signals"] = [ProcessedSignal(**s).model_dump(by_alias=True, mode="json") for s in signals]
    
    # Get associated insights (that reference these signals)
    signal_ids = [s["_id"] for s in signals]
    insights = list(insights_col.find({"signal_ids": {"$in": signal_ids}}))
    result["insights"] = [Insight(**i).model_dump(by_alias=True, mode="json") for i in insights]
    
    return result


@router.get("/articles")
def list_articles(
    source: Optional[str] = Query(None),
    limit: int = Query(20, ge=1, le=100)
) -> List[dict]:
    """List articles."""
    db = get_db()
    articles_col: Collection = db.raw_articles
    
    query = {}
    if source:
        query["source_origin"] = source
    
    cursor = articles_col.find(query).sort("published_at", -1).limit(limit)
    
    articles = []
    for doc in cursor:
        article = RawArticle(**doc)
        articles.append(article.model_dump(by_alias=True, mode="json"))
    
    return articles

