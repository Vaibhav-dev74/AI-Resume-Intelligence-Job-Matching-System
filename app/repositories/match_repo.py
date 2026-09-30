from typing import Optional, List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from app.models.match import MatchResult, MatchEvidence, Recommendation


class MatchRepository:
    @classmethod
    async def create_match(cls, db: AsyncSession, match_obj: MatchResult) -> MatchResult:
        db.add(match_obj)
        await db.flush()
        return match_obj

    @classmethod
    async def get_by_id(cls, db: AsyncSession, match_id: str) -> Optional[MatchResult]:
        query = (
            select(MatchResult)
            .where(MatchResult.id == match_id)
            .options(
                selectinload(MatchResult.evidences).selectinload(MatchEvidence.requirement_skill),
                selectinload(MatchResult.evidences).selectinload(MatchEvidence.matched_candidate_skill),
                selectinload(MatchResult.profile),
                selectinload(MatchResult.job)
            )
        )
        result = await db.execute(query)
        return result.scalar_one_or_none()

    @classmethod
    async def get_by_profile_and_job(cls, db: AsyncSession, profile_id: str, job_id: str) -> Optional[MatchResult]:
        query = (
            select(MatchResult)
            .where(MatchResult.profile_id == profile_id, MatchResult.job_id == job_id)
            .options(
                selectinload(MatchResult.evidences).selectinload(MatchEvidence.requirement_skill),
                selectinload(MatchResult.evidences).selectinload(MatchEvidence.matched_candidate_skill),
                selectinload(MatchResult.profile),
                selectinload(MatchResult.job)
            )
            .order_by(MatchResult.created_at.desc())
        )
        result = await db.execute(query)
        return result.scalars().first()


match_repo = MatchRepository()
