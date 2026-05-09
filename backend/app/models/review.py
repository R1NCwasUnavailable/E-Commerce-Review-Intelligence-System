from pydantic import BaseModel
from typing import List, Dict, Optional

class ReviewRequest(BaseModel):
    text: str

class BulkReviewRequest(BaseModel):
    reviews: List[str]

class ReviewResponse(BaseModel):
    id: Optional[str] = None
    text: str
    sentiment: str
    score: float
    aspects: Dict[str, str] = {}

class SummaryResponse(BaseModel):
    summary: str

class StatsResponse(BaseModel):
    total_reviews: int
    sentiment_distribution: Dict[str, int]

class FeedbackRequest(BaseModel):
    review_id: str
    corrected_sentiment: Optional[str] = None
    corrected_aspects: Optional[Dict[str, str]] = None