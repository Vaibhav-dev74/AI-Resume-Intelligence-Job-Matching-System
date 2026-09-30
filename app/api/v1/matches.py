from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.database import get_db
from app.schemas.match import MatchRequest, MatchResponse, JobRecommendationItem
from app.services.matching_service import matching_service
from app.services.recommendation_service import recommendation_service
from app.repositories.match_repo import match_repo

router = APIRouter(prefix="/matches", tags=["Matching & Analysis"])


@router.post("/analyze", response_model=MatchResponse)
async def analyze_match(
    request: MatchRequest,
    db: AsyncSession = Depends(get_db)
):
    try:
        result = await matching_service.match_resume_with_job(
            db,
            resume_id=request.resume_id,
            job_id=request.job_id,
            job_text=request.job_text
        )
        return MatchResponse(
            id=result["match_id"],
            profile_id=result["profile_id"],
            job_id=result["job_id"],
            scores=result["scores"],
            synthesis_explanation=result["synthesis_explanation"],
            evidences=[
                {
                    "requirement_skill": {
                        "id": "skill_id",
                        "canonical_name": ev["skill_name"],
                        "category": ev.get("category", "tool"),
                        "aliases": []
                    },
                    "match_status": ev["match_status"],
                    "similarity_score": ev["similarity_score"],
                    "evidence_quote": ev.get("evidence_quote"),
                    "explanation": ev["explanation"]
                }
                for ev in result["evidences"]
            ],
            skill_gap_analysis=result["skill_gap_analysis"],
            created_at=result["created_at"]
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Match evaluation failed: {str(e)}")


@router.get("/{match_id}", response_model=MatchResponse)
async def get_match_by_id(match_id: str, db: AsyncSession = Depends(get_db)):
    match = await match_repo.get_by_id(db, match_id)
    if not match:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Match result not found.")

    evidences = [
        {
            "requirement_skill": {
                "id": ev.requirement_skill.id,
                "canonical_name": ev.requirement_skill.canonical_name,
                "category": ev.requirement_skill.category,
                "aliases": ev.requirement_skill.aliases or []
            },
            "match_status": ev.match_status,
            "similarity_score": ev.similarity_score,
            "evidence_quote": ev.evidence_quote,
            "explanation": ev.explanation
        }
        for ev in match.evidences
    ]

    scores = {
        "overall_score": match.overall_score,
        "required_skill_score": match.required_skill_score,
        "preferred_skill_score": match.preferred_skill_score,
        "semantic_score": match.semantic_score,
        "experience_score": match.experience_score,
        "project_score": match.project_score,
        "education_score": match.education_score,
        "scoring_weights": match.scoring_config_snapshot or {}
    }

    return MatchResponse(
        id=match.id,
        profile_id=match.profile_id,
        job_id=match.job_id,
        scores=scores,
        synthesis_explanation=match.synthesis_explanation or "",
        evidences=evidences,
        created_at=match.created_at
    )


@router.get("/recommendations/{resume_id}", response_model=List[JobRecommendationItem])
async def get_recommendations(resume_id: str, top_k: int = 5, db: AsyncSession = Depends(get_db)):
    try:
        recs = await recommendation_service.recommend_jobs_for_candidate(db, resume_id, top_k=top_k)
        return recs
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
