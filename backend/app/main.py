from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import get_settings
from app.database.database import engine, Base
from app.database import models  # noqa: F401 -- ensures models are registered before create_all
from app.api import auth, analysis, history, dashboard

settings = get_settings()

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="VoiceShield AI",
    description="Real-Time Voice Cloning Detection and Impersonation Prevention System",
    version="0.1.0",
)

origins = [origin.strip() for origin in settings.CORS_ORIGINS.split(",")]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(analysis.router)
app.include_router(history.router)
app.include_router(dashboard.router)


@app.get("/api/health")
def health_check():
    return {
        "status": "ok",
        "service": "VoiceShield AI Backend",
        "environment": settings.ENVIRONMENT,
    }


@app.get("/")
def root():
    return {"message": "VoiceShield AI backend is running. Visit /docs for API documentation."}
