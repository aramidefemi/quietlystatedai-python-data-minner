"""Insights API router."""
from datetime import datetime
from typing import Optional, List
from fastapi import APIRouter, Query
from pymongo.collection import Collection
from db.mongo_client import get_db
from db.models import Insight

router = APIRouter()


@router.get("/")
def get_insights(
    topic: Optional[str] = Query(None, description="Filter by topic"),
    since: Optional[str] = Query(None, description="ISO datetime string"),
    limit: int = Query(20, ge=1, le=100)
) -> List[dict]:
    """
    Get recent insights.
    
    Args:
        topic: Optional topic filter
        since: Optional datetime filter (ISO format)
        limit: Maximum number of results
    """
    db = get_db()
    insights_col: Collection = db.insights
    
    query = {}
    if topic:
        query["topic"] = topic
    if since:
        try:
            since_dt = datetime.fromisoformat(since.replace("Z", "+00:00"))
            query["created_at"] = {"$gte": since_dt}
        except ValueError:
            pass
    
    cursor = insights_col.find(query).sort("created_at", -1).limit(limit)
    
    insights = []
    for doc in cursor:
        insight = Insight(**doc)
        insights.append(insight.model_dump(by_alias=True, mode="json"))
    
    return insights


@router.get("/{insight_id}")
def get_insight(insight_id: str) -> dict:
    """Get a specific insight by ID."""
    from bson import ObjectId
    
    db = get_db()
    insights_col: Collection = db.insights
    
    doc = insights_col.find_one({"_id": ObjectId(insight_id)})
    if not doc:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Insight not found")
    
    insight = Insight(**doc)
    return insight.model_dump(by_alias=True, mode="json")

