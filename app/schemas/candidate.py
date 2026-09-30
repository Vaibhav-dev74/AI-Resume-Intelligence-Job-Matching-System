from typing import List, Optional, Dict
from pydantic import BaseModel, Field, ConfigDict
from app.schemas.skill import CandidateSkillResponse


class ExperienceSchema(BaseModel):
    id: Optional[str] = None
    job_title: str
    company: str
    location: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    is_current: bool = False
    duration_months: int = 0
    description: Optional[str] = None
    key_achievements: List[str] = Field(default_factory=list)
    model_config = ConfigDict(from_attributes=True)


class EducationSchema(BaseModel):
    id: Optional[str] = None
    institution: str
    degree: str
    degree_level: int = 3
    field_of_study: Optional[str] = None
    start_year: Optional[int] = None
    graduation_year: Optional[int] = None
    gpa: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)


class ProjectSchema(BaseModel):
    id: Optional[str] = None
    title: str
    description: Optional[str] = None
    technologies_used: List[str] = Field(default_factory=list)
    repo_url: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)


class CertificationSchema(BaseModel):
    id: Optional[str] = None
    name: str
    issuer: Optional[str] = None
    issue_year: Optional[int] = None
    model_config = ConfigDict(from_attributes=True)


class CandidateProfileResponse(BaseModel):
    id: str
    resume_id: str
    full_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    location: Optional[str] = None
    linkedin_url: Optional[str] = None
    github_url: Optional[str] = None
    portfolio_url: Optional[str] = None
    summary: Optional[str] = None
    total_years_experience: float = 0.0
    inferred_primary_role: Optional[str] = None

    skills: List[CandidateSkillResponse] = Field(default_factory=list)
    categorized_skills: Dict[str, List[str]] = Field(default_factory=dict)
    experiences: List[ExperienceSchema] = Field(default_factory=list)
    educations: List[EducationSchema] = Field(default_factory=list)
    projects: List[ProjectSchema] = Field(default_factory=list)
    certifications: List[CertificationSchema] = Field(default_factory=list)
    model_config = ConfigDict(from_attributes=True)
