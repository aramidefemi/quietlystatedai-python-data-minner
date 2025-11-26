"""Pydantic models for database documents."""
from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from bson import ObjectId


class PyObjectId(ObjectId):
    """Custom ObjectId for Pydantic v2."""
    @classmethod
    def __get_pydantic_core_schema__(cls, source_type, handler):
        from pydantic_core import core_schema
        return core_schema.json_or_python_schema(
            json_schema=core_schema.str_schema(),
            python_schema=core_schema.union_schema([
                core_schema.is_instance_schema(ObjectId),
                core_schema.chain_schema([
                    core_schema.str_schema(),
                    core_schema.no_info_plain_validator_function(cls.validate),
                ])
            ]),
            serialization=core_schema.plain_serializer_function_ser_schema(
                lambda x: str(x) if isinstance(x, ObjectId) else x
            ),
        )

    @classmethod
    def validate(cls, v):
        if isinstance(v, ObjectId):
            return v
        if isinstance(v, str):
            if ObjectId.is_valid(v):
                return ObjectId(v)
            raise ValueError("Invalid ObjectId string")
        raise ValueError("Invalid ObjectId")


# Raw data models
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
    source_type: str = "trend"
    source_origin: str
    source_url: str
    group: str
    term: str
    geo: str
    timeframe: str
    pulled_at: datetime = Field(default_factory=datetime.utcnow)
    weekly_interest: float = 0.0
    related_queries: RelatedQueries = Field(default_factory=RelatedQueries)

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True


class RawAlert(BaseModel):
    """Raw alerts document model."""
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    source_type: str = "alert"
    source_origin: str
    source_url: str
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
    source_type: str = "article"
    source_origin: str
    source_url: str
    title: str
    url: str
    published_at: datetime
    fetched_at: datetime = Field(default_factory=datetime.utcnow)
    author: Optional[str] = None
    text: str
    tags_raw: List[str] = Field(default_factory=list)
    data_points: List[str] = Field(default_factory=list)  # Quantifiable statements

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True


# Processed models
class ProcessedSignal(BaseModel):
    """Processed signal document model."""
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    source_type: str  # "article" | "alert" | "trend"
    source_origin: str
    source_url: str
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

