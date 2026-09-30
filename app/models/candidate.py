import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Float, Integer, Boolean, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from app.models.database import Base, UniversalVector


class CandidateProfile(Base):
    __tablename__ = "candidate_profiles"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    resume_id = Column(String(36), ForeignKey("resumes.id", ondelete="CASCADE"), unique=True, nullable=False)
    full_name = Column(String(255), nullable=True)
    email = Column(String(255), nullable=True)
    phone = Column(String(64), nullable=True)
    location = Column(String(255), nullable=True)
    linkedin_url = Column(String(512), nullable=True)
    github_url = Column(String(512), nullable=True)
    portfolio_url = Column(String(512), nullable=True)
    summary = Column(Text, nullable=True)
    total_years_experience = Column(Float, default=0.0)
    inferred_primary_role = Column(String(128), nullable=True)
    embedding = Column(UniversalVector(dim=384), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    resume = relationship("Resume", back_populates="profile")
    skills = relationship("CandidateSkill", back_populates="profile", cascade="all, delete-orphan")
    experiences = relationship("Experience", back_populates="profile", cascade="all, delete-orphan")
    educations = relationship("Education", back_populates="profile", cascade="all, delete-orphan")
    projects = relationship("Project", back_populates="profile", cascade="all, delete-orphan")
    certifications = relationship("Certification", back_populates="profile", cascade="all, delete-orphan")
    match_results = relationship("MatchResult", back_populates="profile", cascade="all, delete-orphan")


class CandidateSkill(Base):
    __tablename__ = "candidate_skills"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    profile_id = Column(String(36), ForeignKey("candidate_profiles.id", ondelete="CASCADE"), nullable=False)
    skill_id = Column(String(36), ForeignKey("skills.id"), nullable=False)
    raw_extracted_text = Column(String(128), nullable=False)
    evidence_context = Column(Text, nullable=True)
    confidence_score = Column(Float, default=1.0)
    years_experience = Column(Float, nullable=True)

    profile = relationship("CandidateProfile", back_populates="skills")
    skill = relationship("Skill", back_populates="candidate_skills")


class Experience(Base):
    __tablename__ = "experiences"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    profile_id = Column(String(36), ForeignKey("candidate_profiles.id", ondelete="CASCADE"), nullable=False)
    job_title = Column(String(255), nullable=False)
    company = Column(String(255), nullable=False)
    location = Column(String(255), nullable=True)
    start_date = Column(String(32), nullable=True)
    end_date = Column(String(32), nullable=True)
    is_current = Column(Boolean, default=False)
    duration_months = Column(Integer, default=0)
    description = Column(Text, nullable=True)
    key_achievements = Column(JSON, default=list)
    embedding = Column(UniversalVector(dim=384), nullable=True)

    profile = relationship("CandidateProfile", back_populates="experiences")


class Education(Base):
    __tablename__ = "educations"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    profile_id = Column(String(36), ForeignKey("candidate_profiles.id", ondelete="CASCADE"), nullable=False)
    institution = Column(String(255), nullable=False)
    degree = Column(String(255), nullable=False)
    degree_level = Column(Integer, default=3)
    field_of_study = Column(String(255), nullable=True)
    start_year = Column(Integer, nullable=True)
    graduation_year = Column(Integer, nullable=True)
    gpa = Column(String(32), nullable=True)

    profile = relationship("CandidateProfile", back_populates="educations")


class Project(Base):
    __tablename__ = "projects"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    profile_id = Column(String(36), ForeignKey("candidate_profiles.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    technologies_used = Column(JSON, default=list)
    repo_url = Column(String(512), nullable=True)
    embedding = Column(UniversalVector(dim=384), nullable=True)

    profile = relationship("CandidateProfile", back_populates="projects")


class Certification(Base):
    __tablename__ = "certifications"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    profile_id = Column(String(36), ForeignKey("candidate_profiles.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(255), nullable=False)
    issuer = Column(String(255), nullable=True)
    issue_year = Column(Integer, nullable=True)

    profile = relationship("CandidateProfile", back_populates="certifications")
