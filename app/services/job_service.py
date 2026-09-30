from typing import Dict, Any, List
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.job import Job, JobRequirement
from app.ai.extraction.job_analyzer import job_analyzer
from app.ai.embeddings.embedding_engine import embedding_engine
from app.repositories.job_repo import job_repo
from app.repositories.skill_repo import skill_repo


class JobService:
    @classmethod
    async def analyze_and_save_job(
        cls,
        db: AsyncSession,
        raw_text: str,
        title: str = None,
        company: str = None
    ) -> Job:
        parsed = job_analyzer.analyze(raw_text, title=title or "", company=company or "")
        job_embedding = embedding_engine.encode(f"{parsed['title']} {parsed['domain']} {parsed['raw_text'][:1000]}")

        job_obj = Job(
            title=parsed["title"],
            company=parsed["company"],
            location=parsed["location"],
            raw_description=parsed["raw_text"],
            min_years_experience=parsed["min_years_experience"],
            min_education_level=parsed["min_education_level"],
            domain=parsed["domain"],
            responsibilities=parsed["responsibilities"],
            embedding=job_embedding.tolist()
        )
        await job_repo.create_job(db, job_obj)

        for sk in parsed["required_skills"]:
            skill_entity = await skill_repo.get_or_create(
                db,
                canonical_name=sk["canonical_name"],
                category=sk["category"]
            )
            req = JobRequirement(
                job_id=job_obj.id,
                skill_id=skill_entity.id,
                is_required=1,
                importance_weight=1.0,
                context_text=sk.get("evidence_context")
            )
            db.add(req)

        for sk in parsed["preferred_skills"]:
            skill_entity = await skill_repo.get_or_create(
                db,
                canonical_name=sk["canonical_name"],
                category=sk["category"]
            )
            req = JobRequirement(
                job_id=job_obj.id,
                skill_id=skill_entity.id,
                is_required=0,
                importance_weight=0.5,
                context_text=sk.get("evidence_context")
            )
            db.add(req)

        await db.flush()
        full_job = await job_repo.get_by_id(db, job_obj.id)
        return full_job


job_service = JobService()
