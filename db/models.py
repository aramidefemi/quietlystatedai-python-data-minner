"""Pydantic models for database documents."""
from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from bson import ObjectId


class PyObjectId(ObjectId):
    """Custom ObjectId for Pydantic."""
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return ObjectId(v)

    @classmethod
    def __modify_schema__(cls, field_schema):
        field_schema.update(type="string")


# Source models
class Source(BaseModel):
    """Source document model."""
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    type: str  # "trend" | "alert" | "article"
    origin: str
    url: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True


# Raw data models
class InterestPoint(BaseModel):
    """Single interest data point."""
    date: datetime
    value: int


class RelatedQuery(BaseModel):
    """Related query entry."""
    query: str
    value: int
    is_breakout: Optional[bool] = False


class RelatedQueries(BaseModel):
    """Related queries container."""
    top: List[RelatedQuery] = Field(default_factory=list)
    rising: List[RelatedQuery] = Field(default_factory=list)


class RawTrend(BaseModel):
    """Raw trends document model."""
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    source_id: PyObjectId
    group: str
    term: str
    geo: str
    timeframe: str
    pulled_at: datetime = Field(default_factory=datetime.utcnow)
    interest_over_time: List[InterestPoint] = Field(default_factory=list)
    related_queries: RelatedQueries = Field(default_factory=RelatedQueries)
    raw_payload: Optional[Dict[str, Any]] = None

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True


class RawAlert(BaseModel):
    """Raw alerts document model."""
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    source_id: PyObjectId
    keyword: str
    title: str
    snippet: str
    url: str
    published_at: datetime
    fetched_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True


class RawArticle(BaseModel):
    """Raw articles document model."""
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    source_id: PyObjectId
    title: str
    url: str
    source: str
    published_at: datetime
    fetched_at: datetime = Field(default_factory=datetime.utcnow)
    author: Optional[str] = None
    text: str
    tags_raw: List[str] = Field(default_factory=list)

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True


# Processed models
class ProcessedSignal(BaseModel):
    """Processed signal document model."""
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    source_id: PyObjectId
    origin_type: str  # "article" | "alert"
    topic: str
    entity: str
    metric: str
    value_now: float
    value_before: Optional[float] = None
    unit: str
    time_ref: str
    context_sentence: str
    model_used: str
    confidence: float
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True


class Insight(BaseModel):
    """Insight document model."""
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    topic: str
    title: str
    summary: str
    implication: str
    target_audience: str
    signal_ids: List[PyObjectId] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    window_start: datetime
    window_end: datetime

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True

