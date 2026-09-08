from sqlalchemy import Column, Integer, String, Float, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(150), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    scans = relationship("Scan", back_populates="owner", cascade="all, delete-orphan")
    logs = relationship("SecurityLog", back_populates="owner", cascade="all, delete-orphan")


class Scan(Base):
    __tablename__ = "scans"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    filename = Column(String(255), nullable=True)

    human_probability = Column(Float, nullable=False)
    ai_probability = Column(Float, nullable=False)
    authenticity_score = Column(Float, nullable=False)

    risk_score = Column(Float, nullable=False)
    risk_level = Column(String(20), nullable=False)  # LOW / MEDIUM / HIGH / CRITICAL

    context_result = Column(Text, nullable=True)   # JSON-encoded string of suspicious indicators
    recommendation = Column(Text, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    owner = relationship("User", back_populates="scans")


class SecurityLog(Base):
    __tablename__ = "security_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)  # nullable: failed logins may have no valid user

    event_type = Column(String(50), nullable=False)  # e.g. LOGIN, FAILED_LOGIN, SCAN, HIGH_RISK, CRITICAL_RISK
    description = Column(Text, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    owner = relationship("User", back_populates="logs")