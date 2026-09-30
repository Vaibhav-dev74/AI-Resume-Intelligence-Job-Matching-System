from typing import List, Optional
from pydantic import BaseModel, Field, ConfigDict
from app.core.constants import SkillCategory, MatchStatus


class SkillBase(BaseModel):
    canonical_name: str
    category: SkillCategory
    aliases: List[str] = Field(default_factory=list)
    description: Optional[str] = None


class SkillCreate(SkillBase):
    pass


class SkillResponse(SkillBase):
    id: str
    model_config = ConfigDict(from_attributes=True)


class CandidateSkillResponse(BaseModel):
    id: str
    skill: SkillResponse
    raw_extracted_text: str
    evidence_context: Optional[str] = None
    confidence_score: float = 1.0
    years_experience: Optional[float] = None
    model_config = ConfigDict(from_attributes=True)


class SkillGapItem(BaseModel):
    skill_name: str
    category: str
    is_required: bool
    status: MatchStatus
    matched_transferable_skill: Optional[str] = None
    similarity_score: float = 0.0
    importance_weight: float = 1.0
    priority_level: str
    learning_difficulty: str
    rationale: str


class SkillGapAnalysisResponse(BaseModel):
    strong_skills: List[SkillGapItem] = Field(default_factory=list)
    transferable_skills: List[SkillGapItem] = Field(default_factory=list)
    inferred_skills: List[SkillGapItem] = Field(default_factory=list)
    missing_skills: List[SkillGapItem] = Field(default_factory=list)
    total_required_skills: int
    matched_required_skills: int
    coverage_ratio: float
