import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Float, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from app.models.database import Base


class MatchResult(Base):
    __tablename__ = "match_results"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    profile_id = Column(String(36), ForeignKey("candidate_profiles.id", ondelete="CASCADE"), nullable=False)
    job_id = Column(String(36), ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False)
    
    overall_score = Column(Float, nullable=False)
    required_skill_score = Column(Float, nullable=False)
    preferred_skill_score = Column(Float, nullable=False)
    semantic_score = Column(Float, nullable=False)
    experience_score = Column(Float, nullable=False)
    project_score = Column(Float, nullable=False)
    education_score = Column(Float, nullable=False)
    
    scoring_config_snapshot = Column(JSON, default=dict)
    synthesis_explanation = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    profile = relationship("CandidateProfile", back_populates="match_results")
    job = relationship("Job", back_populates="match_results")
    evidences = relationship("MatchEvidence", back_populates="match_result", cascade="all, delete-orphan")


class MatchEvidence(Base):
    __tablename__ = "match_evidences"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    match_id = Column(String(36), ForeignKey("match_results.id", ondelete="CASCADE"), nullable=False)
    requirement_skill_id = Column(String(36), ForeignKey("skills.id"), nullable=False)
    matched_candidate_skill_id = Column(String(36), ForeignKey("skills.id"), nullable=True)
    
    match_status = Column(String(32), nullable=False)
    similarity_score = Column(Float, default=0.0)
    evidence_quote = Column(Text, nullable=True)
    explanation = Column(Text, nullable=False)

    match_result = relationship("MatchResult", back_populates="evidences")
    requirement_skill = relationship("Skill", foreign_keys=[requirement_skill_id])
    matched_candidate_skill = relationship("Skill", foreign_keys=[matched_candidate_skill_id])


class Recommendation(Base):
    __tablename__ = "recommendations"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    profile_id = Column(String(36), ForeignKey("candidate_profiles.id", ondelete="CASCADE"), nullable=False)
    job_id = Column(String(36), ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False)
    relevance_score = Column(Float, nullable=False)
    rank = Column(Float, nullable=False)
    match_rationale = Column(Text, nullable=False)
    key_strengths = Column(JSON, default=list)
    key_gaps = Column(JSON, default=list)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
