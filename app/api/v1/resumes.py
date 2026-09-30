from typing import List
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.database import get_db
from app.schemas.resume import ResumeUploadResponse, ResumeDetailResponse, ResumeImprovementResponse
from app.services.resume_service import resume_service
from app.repositories.resume_repo import resume_repo
from app.ai.recommendations.resume_improver import resume_improver

router = APIRouter(prefix="/resumes", tags=["Resumes"])


@router.post("/upload", response_model=ResumeUploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_resume(
    file: UploadFile = File(..., description="PDF or DOCX resume document"),
    db: AsyncSession = Depends(get_db)
):
    file_bytes = await file.read()
    try:
        resume = await resume_service.process_and_save_resume(db, file_bytes, file.filename)
        profile_data = None
        if resume.profile:
            profile_data = {
                "id": resume.profile.id,
                "resume_id": resume.id,
                "full_name": resume.profile.full_name,
                "email": resume.profile.email,
                "phone": resume.profile.phone,
                "location": resume.profile.location,
                "linkedin_url": resume.profile.linkedin_url,
                "github_url": resume.profile.github_url,
                "portfolio_url": resume.profile.portfolio_url,
                "summary": resume.profile.summary,
                "total_years_experience": resume.profile.total_years_experience,
                "inferred_primary_role": resume.profile.inferred_primary_role,
                "skills": [
                    {
                        "id": cs.id,
                        "skill": {
                            "id": cs.skill.id,
                            "canonical_name": cs.skill.canonical_name,
                            "category": cs.skill.category,
                            "aliases": cs.skill.aliases or [],
                            "description": cs.skill.description
                        },
                        "raw_extracted_text": cs.raw_extracted_text,
                        "evidence_context": cs.evidence_context,
                        "confidence_score": cs.confidence_score,
                        "years_experience": cs.years_experience
                    }
                    for cs in resume.profile.skills
                ],
                "categorized_skills": {},
                "experiences": [
                    {
                        "id": exp.id,
                        "job_title": exp.job_title,
                        "company": exp.company,
                        "location": exp.location,
                        "start_date": exp.start_date,
                        "end_date": exp.end_date,
                        "is_current": exp.is_current,
                        "duration_months": exp.duration_months,
                        "description": exp.description,
                        "key_achievements": exp.key_achievements or []
                    }
                    for exp in resume.profile.experiences
                ],
                "educations": [
                    {
                        "id": edu.id,
                        "institution": edu.institution,
                        "degree": edu.degree,
                        "degree_level": edu.degree_level,
                        "field_of_study": edu.field_of_study,
                        "start_year": edu.start_year,
                        "graduation_year": edu.graduation_year,
                        "gpa": edu.gpa
                    }
                    for edu in resume.profile.educations
                ],
                "projects": [
                    {
                        "id": p.id,
                        "title": p.title,
                        "description": p.description,
                        "technologies_used": p.technologies_used or [],
                        "repo_url": p.repo_url
                    }
                    for p in resume.profile.projects
                ],
                "certifications": []
            }

        return ResumeUploadResponse(
            id=resume.id,
            file_name=resume.file_name,
            file_size_bytes=resume.file_size_bytes,
            mime_type=resume.mime_type,
            processing_status=resume.processing_status,
            message="Resume successfully uploaded, sanitized, and parsed into structured candidate profile.",
            profile=profile_data
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to process resume: {str(e)}")


@router.get("", response_model=List[ResumeDetailResponse])
async def list_resumes(limit: int = 50, offset: int = 0, db: AsyncSession = Depends(get_db)):
    resumes = await resume_repo.list_all(db, limit=limit, offset=offset)
    return resumes


@router.get("/{resume_id}", response_model=ResumeDetailResponse)
async def get_resume(resume_id: str, db: AsyncSession = Depends(get_db)):
    resume = await resume_repo.get_by_id(db, resume_id)
    if not resume:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resume not found.")
    return resume


@router.delete("/{resume_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_resume(resume_id: str, db: AsyncSession = Depends(get_db)):
    deleted = await resume_repo.delete(db, resume_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resume not found.")
    return None


@router.post("/{resume_id}/improve", response_model=ResumeImprovementResponse)
async def improve_resume(resume_id: str, db: AsyncSession = Depends(get_db)):
    resume = await resume_repo.get_by_id(db, resume_id)
    if not resume or not resume.profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resume or profile not found.")

    profile = resume.profile
    cand_dict = {
        "skills": [{"canonical_name": cs.skill.canonical_name} for cs in profile.skills],
        "experiences": [
            {"company": exp.company, "key_achievements": exp.key_achievements or []}
            for exp in profile.experiences
        ],
        "projects": [
            {"title": p.title, "description": p.description or ""}
            for p in profile.projects
        ],
        "summary": profile.summary
    }

    result = resume_improver.improve(cand_dict)
    return result
