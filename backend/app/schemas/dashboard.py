from pydantic import BaseModel
from typing import Dict


class DashboardStats(BaseModel):
    total_scans: int
    real_voice_count: int
    ai_voice_count: int
    high_risk_count: int
    critical_risk_count: int
    risk_distribution: Dict[str, int]  # {"LOW": x, "MEDIUM": x, "HIGH": x, "CRITICAL": x}
    average_risk_score: float