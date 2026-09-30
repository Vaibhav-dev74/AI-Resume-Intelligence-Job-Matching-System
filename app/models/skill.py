import uuid
from sqlalchemy import Column, String, Float, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from app.models.database import Base, UniversalVector


class Skill(Base):
    __tablename__ = "skills"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    canonical_name = Column(String(128), unique=True, index=True, nullable=False)
    category = Column(String(64), index=True, nullable=False)
    aliases = Column(JSON, default=list)
    description = Column(Text, nullable=True)
    embedding = Column(UniversalVector(dim=384), nullable=True)

    candidate_skills = relationship("CandidateSkill", back_populates="skill")
    job_requirements = relationship("JobRequirement", back_populates="skill")

    outgoing_relations = relationship(
        "SkillRelation",
        foreign_keys="SkillRelation.source_skill_id",
        back_populates="source_skill",
        cascade="all, delete-orphan"
    )
    incoming_relations = relationship(
        "SkillRelation",
        foreign_keys="SkillRelation.target_skill_id",
        back_populates="target_skill",
        cascade="all, delete-orphan"
    )


class SkillRelation(Base):
    __tablename__ = "skill_relations"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    source_skill_id = Column(String(36), ForeignKey("skills.id", ondelete="CASCADE"), nullable=False)
    target_skill_id = Column(String(36), ForeignKey("skills.id", ondelete="CASCADE"), nullable=False)
    relation_type = Column(String(32), default="TRANSFERABLE")
    transferability_weight = Column(Float, default=0.75)

    source_skill = relationship("Skill", foreign_keys=[source_skill_id], back_populates="outgoing_relations")
    target_skill = relationship("Skill", foreign_keys=[target_skill_id], back_populates="incoming_relations")
