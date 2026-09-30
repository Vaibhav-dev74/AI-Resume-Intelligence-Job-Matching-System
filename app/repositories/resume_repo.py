import uuid
from typing import Optional, List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from app.models.resume import Resume
from app.models.candidate import CandidateProfile, CandidateSkill, Experience, Education, Project, Certification


class ResumeRepository:
    @classmethod
    async def create_resume(cls, db: AsyncSession, resume_obj: Resume) -> Resume:
        db.add(resume_obj)
        await db.flush()
        return resume_obj

    @classmethod
    async def get_by_id(cls, db: AsyncSession, resume_id: str) -> Optional[Resume]:
        query = (
            select(Resume)
            .where(Resume.id == resume_id)
            .options(
                selectinload(Resume.profile).selectinload(CandidateProfile.skills).selectinload(CandidateSkill.skill),
                selectinload(Resume.profile).selectinload(CandidateProfile.experiences),
                selectinload(Resume.profile).selectinload(CandidateProfile.educations),
                selectinload(Resume.profile).selectinload(CandidateProfile.projects),
                selectinload(Resume.profile).selectinload(CandidateProfile.certifications)
            )
        )
        result = await db.execute(query)
        return result.scalar_one_or_none()

    @classmethod
    async def list_all(cls, db: AsyncSession, limit: int = 50, offset: int = 0) -> List[Resume]:
        query = (
            select(Resume)
            .options(
                selectinload(Resume.profile).selectinload(CandidateProfile.skills).selectinload(CandidateSkill.skill),
                selectinload(Resume.profile).selectinload(CandidateProfile.experiences),
                selectinload(Resume.profile).selectinload(CandidateProfile.educations),
                selectinload(Resume.profile).selectinload(CandidateProfile.projects)
            )
            .order_by(Resume.created_at.desc())
            .offset(offset)
            .limit(limit)
        )
        result = await db.execute(query)
        return list(result.scalars().all())

    @classmethod
    async def delete(cls, db: AsyncSession, resume_id: str) -> bool:
        resume = await cls.get_by_id(db, resume_id)
        if not resume:
            return False
        await db.delete(resume)
        await db.flush()
        return True


resume_repo = ResumeRepository()
