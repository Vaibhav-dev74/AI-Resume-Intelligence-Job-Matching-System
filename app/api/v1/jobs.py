from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.database import get_db
from app.schemas.job import JobAnalysisRequest, JobResponse
from app.services.job_service import job_service
from app.repositories.job_repo import job_repo

router = APIRouter(prefix="/jobs", tags=["Jobs"])


@router.post("/analyze", response_model=JobResponse, status_code=status.HTTP_201_CREATED)
async def analyze_job(
    request: JobAnalysisRequest,
    db: AsyncSession = Depends(get_db)
):
    try:
        job = await job_service.analyze_and_save_job(
            db,
            raw_text=request.raw_text,
            title=request.title,
            company=request.company
        )
        req_skills = [
            {
                "id": req.skill.id,
                "canonical_name": req.skill.canonical_name,
                "category": req.skill.category,
                "aliases": req.skill.aliases or [],
                "description": req.skill.description
            }
            for req in job.requirements if req.is_required
        ]
        pref_skills = [
            {
                "id": req.skill.id,
                "canonical_name": req.skill.canonical_name,
                "category": req.skill.category,
                "aliases": req.skill.aliases or [],
                "description": req.skill.description
            }
            for req in job.requirements if not req.is_required
        ]

        return JobResponse(
            id=job.id,
            title=job.title,
            company=job.company,
            location=job.location,
            min_years_experience=job.min_years_experience,
            min_education_level=job.min_education_level,
            domain=job.domain,
            responsibilities=job.responsibilities or [],
            required_skills=req_skills,
            preferred_skills=pref_skills,
            created_at=job.created_at
        )
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Failed to analyze job: {str(e)}")


@router.get("", response_model=List[JobResponse])
async def list_jobs(limit: int = 50, offset: int = 0, db: AsyncSession = Depends(get_db)):
    jobs = await job_repo.list_all(db, limit=limit, offset=offset)
    result = []
    for job in jobs:
        req_skills = [
            {
                "id": req.skill.id,
                "canonical_name": req.skill.canonical_name,
                "category": req.skill.category,
                "aliases": req.skill.aliases or [],
                "description": req.skill.description
            }
            for req in job.requirements if req.is_required
        ]
        pref_skills = [
            {
                "id": req.skill.id,
                "canonical_name": req.skill.canonical_name,
                "category": req.skill.category,
                "aliases": req.skill.aliases or [],
                "description": req.skill.description
            }
            for req in job.requirements if not req.is_required
        ]
        result.append(
            JobResponse(
                id=job.id,
                title=job.title,
                company=job.company,
                location=job.location,
                min_years_experience=job.min_years_experience,
                min_education_level=job.min_education_level,
                domain=job.domain,
                responsibilities=job.responsibilities or [],
                required_skills=req_skills,
                preferred_skills=pref_skills,
                created_at=job.created_at
            )
        )
    return result


@router.get("/{job_id}", response_model=JobResponse)
async def get_job(job_id: str, db: AsyncSession = Depends(get_db)):
    job = await job_repo.get_by_id(db, job_id)
    if not job:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found.")
    req_skills = [
        {
            "id": req.skill.id,
            "canonical_name": req.skill.canonical_name,
            "category": req.skill.category,
            "aliases": req.skill.aliases or [],
            "description": req.skill.description
        }
        for req in job.requirements if req.is_required
    ]
    pref_skills = [
        {
            "id": req.skill.id,
            "canonical_name": req.skill.canonical_name,
            "category": req.skill.category,
            "aliases": req.skill.aliases or [],
            "description": req.skill.description
        }
        for req in job.requirements if not req.is_required
    ]
    return JobResponse(
        id=job.id,
        title=job.title,
        company=job.company,
        location=job.location,
        min_years_experience=job.min_years_experience,
        min_education_level=job.min_education_level,
        domain=job.domain,
        responsibilities=job.responsibilities or [],
        required_skills=req_skills,
        preferred_skills=pref_skills,
        created_at=job.created_at
    )
