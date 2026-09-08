import json
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.database.models import User, Scan
from app.api.auth import get_current_user
from app.schemas.analysis import AnalysisResponse, ScanSummary

router = APIRouter(prefix="/api/history", tags=["History"])


@router.get("", response_model=List[ScanSummary])
def get_history(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Returns all scans belonging to the current user, most recent first.
    """
    scans = (
        db.query(Scan)
        .filter(Scan.user_id == current_user.id)
        .order_by(Scan.created_at.desc())
        .all()
    )
    return scans


@router.get("/{scan_id}", response_model=AnalysisResponse)
def get_scan_detail(
    scan_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Returns full detail for a single scan, only if it belongs to the
    current user.
    """
    scan = (
        db.query(Scan)
        .filter(Scan.id == scan_id, Scan.user_id == current_user.id)
        .first()
    )
    if not scan:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Scan not found")

    indicators = json.loads(scan.context_result) if scan.context_result else []

    return AnalysisResponse(
        scan_id=scan.id,
        filename=scan.filename,
        human_probability=scan.human_probability,
        ai_probability=scan.ai_probability,
        authenticity_score=scan.authenticity_score,
        risk_score=scan.risk_score,
        risk_level=scan.risk_level,
        indicators=indicators,
        recommendation=scan.recommendation,
        actions=[],  # actions aren't stored separately; recompute if needed
        created_at=scan.created_at,
    )


@router.delete("/{scan_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_scan(
    scan_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Deletes a scan record, only if it belongs to the current user.
    """
    scan = (
        db.query(Scan)
        .filter(Scan.id == scan_id, Scan.user_id == current_user.id)
        .first()
    )
    if not scan:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Scan not found")

    db.delete(scan)
    db.commit()
    return None