from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field, field_validator


SUPPORTED_MODELS = {"tfidf", "bm25", "semantic", "hybrid", "structured"}


class SearchRequest(BaseModel):
    query: str = Field(
        ...,
        description="Natural-language search query"
    )
    top_k: int = Field(
        default=10,
        ge=1,
        le=50,
        description="Number of results to retrieve (1 to 50)"
    )
    model: str = Field(
        default="structured",
        description="Retrieval model to use: tfidf, bm25, semantic, hybrid, or structured"
    )

    @field_validator("query")
    @classmethod
    def validate_query_not_empty(cls, v: str) -> str:
        cleaned = v.strip()
        if not cleaned:
            raise ValueError("Query must not be empty or whitespace only.")
        return cleaned

    @field_validator("model")
    @classmethod
    def validate_model_supported(cls, v: str) -> str:
        lowered = v.lower().strip()
        if lowered not in SUPPORTED_MODELS:
            raise ValueError(
                f"Unsupported model '{v}'. Supported models are: {', '.join(sorted(SUPPORTED_MODELS))}"
            )
        return lowered


class SearchResultItem(BaseModel):
    rank: int
    event_id: str
    title: str
    description: Optional[str] = None
    category: Optional[str] = None
    subcategory: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    venue: Optional[str] = None
    start_date: Optional[str] = None
    start_time: Optional[str] = None
    price: Optional[int] = None
    currency: Optional[str] = None
    is_free: Optional[bool] = None
    organizer: Optional[str] = None
    audience: Optional[str] = None
    rating: Optional[float] = None
    score: float

    # Additional explainability attributes for structured ranking
    hybrid_score: Optional[float] = None
    structured_score: Optional[float] = None
    final_score: Optional[float] = None
    matched_signals: Optional[Dict[str, Any]] = None
    signal_contributions: Optional[Dict[str, Any]] = None


class SearchResponse(BaseModel):
    query: str
    model: str
    total_results: int
    results: List[SearchResultItem]


class EventDetailResponse(BaseModel):
    event_id: str
    title: str
    description: Optional[str] = None
    category: Optional[str] = None
    subcategory: Optional[str] = None
    tags: Optional[str] = None
    event_type: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    venue: Optional[str] = None
    address: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    start_date: Optional[str] = None
    start_time: Optional[str] = None
    end_date: Optional[str] = None
    end_time: Optional[str] = None
    price: Optional[int] = None
    currency: Optional[str] = None
    is_free: Optional[bool] = None
    organizer: Optional[str] = None
    expected_attendees: Optional[int] = None
    audience: Optional[str] = None
    language: Optional[str] = None
    rating: Optional[float] = None


class CategoryItem(BaseModel):
    category: str
    count: int


class LocationItem(BaseModel):
    city: str
    state: Optional[str] = None
    count: int

