from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, ConfigDict
from app.schemas.candidate import CandidateProfileResponse


class ResumeUploadResponse(BaseModel):
    id: str
    file_name: str
    file_size_bytes: int
    mime_type: str
    processing_status: str
    message: str
    profile: Optional[CandidateProfileResponse] = None
    model_config = ConfigDict(from_attributes=True)


class ResumeDetailResponse(BaseModel):
    id: str
    file_name: str
    file_size_bytes: int
    mime_type: str
    raw_text: str
    anonymized_text: Optional[str] = None
    processing_status: str
    created_at: datetime
    profile: Optional[CandidateProfileResponse] = None
    model_config = ConfigDict(from_attributes=True)


class ResumeImprovementItem(BaseModel):
    section: str
    original_text: str
    critique: str
    suggested_revision: str
    issue_type: str
    rationale: str
    interactive_prompt: Optional[str] = None


class ResumeImprovementResponse(BaseModel):
    overall_critique: str
    strength_score: float
    suggestions: List[ResumeImprovementItem]
    formatting_insights: List[str]
