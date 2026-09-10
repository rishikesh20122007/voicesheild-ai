import json

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.database.models import User, Scan, SecurityLog
from app.api.auth import get_current_user
from app.schemas.analysis import AnalysisResponse
from app.utils.helpers import generate_temp_filepath, delete_temp_file
from app.services.audio_processor import load_and_preprocess_audio, AudioProcessingError
from app.services.feature_extractor import extract_features, FeatureExtractionError
from app.services.voice_detector import get_voice_detector, VoiceDetectionError
from app.services.context_analyzer import analyze_context
from app.services.risk_engine import get_risk_breakdown
from app.services.prevention_engine import get_prevention_response

router = APIRouter(prefix="/api/analyze", tags=["Analysis"])

ALLOWED_EXTENSIONS = {".wav", ".mp3", ".m4a", ".flac", ".ogg", ".webm"}
MAX_FILE_SIZE_BYTES = 20 * 1024 * 1024  # 20 MB


@router.post("/upload", response_model=AnalysisResponse, status_code=status.HTTP_201_CREATED)
async def analyze_audio(
    file: UploadFile = File(...),
    transcript: str = Form(default=None),
    description: str = Form(default=None),
    transaction_amount: float = Form(default=None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Accepts an uploaded audio file plus optional context, runs the full
    detection pipeline, saves the result, and returns the analysis.

    Privacy note: the uploaded audio is written to a temporary file only
    for the duration of processing, then deleted. Only the derived
    analysis metadata is stored in the database -- never the raw audio.
    """
    import os
    ext = os.path.splitext(file.filename or "")[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file type '{ext}'. Allowed: {', '.join(sorted(ALLOWED_EXTENSIONS))}",
        )

    contents = await file.read()
    if len(contents) > MAX_FILE_SIZE_BYTES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File too large. Maximum size is 20MB.",
        )

    temp_path = generate_temp_filepath(extension=ext)

    try:
        with open(temp_path, "wb") as f:
            f.write(contents)

        # --- Run the full pipeline ---
        try:
            audio, sr = load_and_preprocess_audio(temp_path)
        except AudioProcessingError as exc:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))

        try:
            features = extract_features(audio, sr)
        except FeatureExtractionError as exc:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc))

        try:
            detector = get_voice_detector()
            human_prob, ai_prob = detector.predict(audio, sr, features)
        except VoiceDetectionError as exc:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc))

        context = analyze_context(
            transcript=transcript,
            description=description,
            transaction_amount=transaction_amount,
        )

        breakdown = get_risk_breakdown(ai_prob, context["context_risk_points"])
        prevention = get_prevention_response(breakdown["risk_level"])

        authenticity_score = round(human_prob * 100, 1)

        # --- Save to database ---
        scan = Scan(
            user_id=current_user.id,
            filename=file.filename,
            human_probability=round(human_prob * 100, 1),
            ai_probability=round(ai_prob * 100, 1),
            authenticity_score=authenticity_score,
            risk_score=breakdown["final_risk_score"],
            risk_level=breakdown["risk_level"],
            context_result=json.dumps(context["indicators"]),
            recommendation=prevention["recommendation"],
        )
        db.add(scan)
        db.commit()
        db.refresh(scan)

        # --- Security logging ---
        log_event_type = "SCAN"
        if breakdown["risk_level"] == "HIGH":
            log_event_type = "HIGH_RISK"
        elif breakdown["risk_level"] == "CRITICAL":
            log_event_type = "CRITICAL_RISK"

        db.add(SecurityLog(
            user_id=current_user.id,
            event_type=log_event_type,
            description=f"Scan #{scan.id}: {breakdown['risk_level']} risk ({breakdown['final_risk_score']}/100)",
        ))
        db.commit()

        return AnalysisResponse(
            scan_id=scan.id,
            filename=scan.filename,
            human_probability=scan.human_probability,
            ai_probability=scan.ai_probability,
            authenticity_score=scan.authenticity_score,
            risk_score=scan.risk_score,
            risk_level=scan.risk_level,
            indicators=context["indicators"],
            recommendation=scan.recommendation,
            actions=prevention["actions"],
            created_at=scan.created_at,
        )

    finally:
        # Privacy rule: always delete the temp audio file, even if
        # something above failed.
        delete_temp_file(temp_path)
