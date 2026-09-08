from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import List, Optional


class AnalysisRequest(BaseModel):
    """Optional context fields sent alongside the audio file (as form fields)."""
    transcript: Optional[str] = None
    description: Optional[str] = None
    transaction_amount: Optional[float] = None


class AnalysisResponse(BaseModel):
    scan_id: int
    filename: Optional[str] = None

    human_probability: float
    ai_probability: float
    authenticity_score: float

    risk_score: float
    risk_level: str

    indicators: List[str]
    recommendation: str
    actions: List[str]

    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ScanSummary(BaseModel):
    id: int
    filename: Optional[str] = None
    human_probability: float
    ai_probability: float
    risk_score: float
    risk_level: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)