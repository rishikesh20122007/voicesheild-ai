from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database.database import get_db
from app.database.models import User, Scan
from app.api.auth import get_current_user
from app.schemas.dashboard import DashboardStats

router = APIRouter(prefix="/api/dashboard", tags=["Dashboard"])


@router.get("/stats", response_model=DashboardStats)
def get_dashboard_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Returns aggregate statistics for the current user's scans, used to
    populate the security dashboard.
    """
    scans = db.query(Scan).filter(Scan.user_id == current_user.id).all()

    total_scans = len(scans)

    if total_scans == 0:
        return DashboardStats(
            total_scans=0,
            real_voice_count=0,
            ai_voice_count=0,
            high_risk_count=0,
            critical_risk_count=0,
            risk_distribution={"LOW": 0, "MEDIUM": 0, "HIGH": 0, "CRITICAL": 0},
            average_risk_score=0.0,
        )

    real_voice_count = sum(1 for s in scans if s.human_probability >= 50)
    ai_voice_count = sum(1 for s in scans if s.human_probability < 50)
    high_risk_count = sum(1 for s in scans if s.risk_level == "HIGH")
    critical_risk_count = sum(1 for s in scans if s.risk_level == "CRITICAL")

    risk_distribution = {"LOW": 0, "MEDIUM": 0, "HIGH": 0, "CRITICAL": 0}
    for s in scans:
        if s.risk_level in risk_distribution:
            risk_distribution[s.risk_level] += 1

    average_risk_score = round(sum(s.risk_score for s in scans) / total_scans, 1)

    return DashboardStats(
        total_scans=total_scans,
        real_voice_count=real_voice_count,
        ai_voice_count=ai_voice_count,
        high_risk_count=high_risk_count,
        critical_risk_count=critical_risk_count,
        risk_distribution=risk_distribution,
        average_risk_score=average_risk_score,
    )