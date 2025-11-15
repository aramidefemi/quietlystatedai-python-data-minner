"""Signals API router."""
from datetime import datetime
from typing import Optional, List
from fastapi import APIRouter, Query
from pymongo.collection import Collection
from db.mongo_client import get_db
from db.models import ProcessedSignal

router = APIRouter()


@router.get("/")
def get_signals(
    topic: Optional[str] = Query(None, description="Filter by topic"),
    since: Optional[str] = Query(None, description="ISO datetime string"),
    limit: int = Query(50, ge=1, le=200)
) -> List[dict]:
    """
    Get processed signals.
    
    Args:
        topic: Optional topic filter
        since: Optional datetime filter (ISO format)
        limit: Maximum number of results
    """
    db = get_db()
    signals_col: Collection = db.processed_signals
    
    query = {}
    if topic:
        query["topic"] = topic
    if since:
        try:
            since_dt = datetime.fromisoformat(since.replace("Z", "+00:00"))
            query["created_at"] = {"$gte": since_dt}
        except ValueError:
            pass
    
    cursor = signals_col.find(query).sort("created_at", -1).limit(limit)
    
    signals = []
    for doc in cursor:
        signal = ProcessedSignal(**doc)
        signals.append(signal.model_dump(by_alias=True, mode="json"))
    
    return signals


@router.get("/{signal_id}")
def get_signal(signal_id: str) -> dict:
    """Get a specific signal by ID."""
    from bson import ObjectId
    
    db = get_db()
    signals_col: Collection = db.processed_signals
    
    doc = signals_col.find_one({"_id": ObjectId(signal_id)})
    if not doc:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Signal not found")
    
    signal = ProcessedSignal(**doc)
    return signal.model_dump(by_alias=True, mode="json")

