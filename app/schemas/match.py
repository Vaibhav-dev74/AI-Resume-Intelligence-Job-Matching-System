from typing import List, Optional, Dict
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict
from app.schemas.skill import SkillResponse, SkillGapAnalysisResponse


class MatchRequest(BaseModel):
    resume_id: str
    job_id: Optional[str] = None
    job_text: Optional[str] = None


class MatchEvidenceSchema(BaseModel):
    requirement_skill: SkillResponse
    match_status: str
    similarity_score: float
    evidence_quote: Optional[str] = None
    explanation: str
    model_config = ConfigDict(from_attributes=True)


class MatchScoreBreakdown(BaseModel):
    overall_score: float
    required_skill_score: float
    preferred_skill_score: float
    semantic_score: float
    experience_score: float
    project_score: float
    education_score: float
    scoring_weights: Dict[str, float]


class MatchResponse(BaseModel):
    id: str
    profile_id: str
    job_id: str
    scores: MatchScoreBreakdown
    synthesis_explanation: str
    evidences: List[MatchEvidenceSchema] = Field(default_factory=list)
    skill_gap_analysis: Optional[SkillGapAnalysisResponse] = None
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


class JobRecommendationItem(BaseModel):
    job_id: str
    title: str
    company: str
    overall_fit_score: float
    rank: int
    match_rationale: str
    matched_skills: List[str]
    missing_skills: List[str]
    transferable_skills: List[str]
