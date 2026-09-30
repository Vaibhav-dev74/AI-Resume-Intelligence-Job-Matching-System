from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict
from app.schemas.skill import SkillResponse


class JobRequirementSchema(BaseModel):
    id: Optional[str] = None
    skill: SkillResponse
    is_required: bool = True
    importance_weight: float = 1.0
    context_text: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)


class JobAnalysisRequest(BaseModel):
    title: Optional[str] = None
    company: Optional[str] = None
    raw_text: str = Field(..., min_length=20, description="Plain text job description to analyze")


class JobResponse(BaseModel):
    id: str
    title: str
    company: str
    location: Optional[str] = None
    min_years_experience: float
    min_education_level: int
    domain: Optional[str] = None
    responsibilities: List[str] = Field(default_factory=list)
    required_skills: List[SkillResponse] = Field(default_factory=list)
    preferred_skills: List[SkillResponse] = Field(default_factory=list)
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)
