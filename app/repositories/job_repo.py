from typing import Optional, List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from app.models.job import Job, JobRequirement
from app.models.skill import Skill


class JobRepository:
    @classmethod
    async def create_job(cls, db: AsyncSession, job_obj: Job) -> Job:
        db.add(job_obj)
        await db.flush()
        return job_obj

    @classmethod
    async def get_by_id(cls, db: AsyncSession, job_id: str) -> Optional[Job]:
        query = (
            select(Job)
            .where(Job.id == job_id)
            .options(
                selectinload(Job.requirements).selectinload(JobRequirement.skill)
            )
        )
        result = await db.execute(query)
        return result.scalar_one_or_none()

    @classmethod
    async def list_all(cls, db: AsyncSession, limit: int = 50, offset: int = 0) -> List[Job]:
        query = (
            select(Job)
            .options(
                selectinload(Job.requirements).selectinload(JobRequirement.skill)
            )
            .order_by(Job.created_at.desc())
            .offset(offset)
            .limit(limit)
        )
        result = await db.execute(query)
        return list(result.scalars().all())

    @classmethod
    async def delete(cls, db: AsyncSession, job_id: str) -> bool:
        job = await cls.get_by_id(db, job_id)
        if not job:
            return False
        await db.delete(job)
        await db.flush()
        return True


job_repo = JobRepository()
