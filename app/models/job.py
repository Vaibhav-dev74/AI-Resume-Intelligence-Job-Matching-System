import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Float, Integer, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from app.models.database import Base, UniversalVector


class Job(Base):
    __tablename__ = "jobs"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String(255), nullable=False)
    company = Column(String(255), nullable=False)
    location = Column(String(255), nullable=True)
    raw_description = Column(Text, nullable=False)
    min_years_experience = Column(Float, default=0.0)
    min_education_level = Column(Integer, default=3)
    domain = Column(String(128), nullable=True)
    responsibilities = Column(JSON, default=list)
    embedding = Column(UniversalVector(dim=384), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    requirements = relationship("JobRequirement", back_populates="job", cascade="all, delete-orphan")
    match_results = relationship("MatchResult", back_populates="job", cascade="all, delete-orphan")


class JobRequirement(Base):
    __tablename__ = "job_requirements"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    job_id = Column(String(36), ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False)
    skill_id = Column(String(36), ForeignKey("skills.id"), nullable=False)
    is_required = Column(Integer, default=1)
    importance_weight = Column(Float, default=1.0)
    context_text = Column(Text, nullable=True)

    job = relationship("Job", back_populates="requirements")
    skill = relationship("Skill", back_populates="job_requirements")
