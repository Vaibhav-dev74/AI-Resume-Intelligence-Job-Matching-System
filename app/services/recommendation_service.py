from typing import List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.resume_repo import resume_repo
from app.repositories.job_repo import job_repo
from app.ai.recommendations.job_recommender import job_recommender


class RecommendationService:
    @classmethod
    async def recommend_jobs_for_candidate(
        cls,
        db: AsyncSession,
        resume_id: str,
        top_k: int = 5
    ) -> List[Dict[str, Any]]:
        resume = await resume_repo.get_by_id(db, resume_id)
        if not resume or not resume.profile:
            raise ValueError(f"Resume with id '{resume_id}' not found or profile is unparsed.")

        profile = resume.profile
        cand_dict = {
            "summary": profile.summary,
            "total_years_experience": profile.total_years_experience,
            "skills": [
                {
                    "canonical_name": cs.skill.canonical_name,
                    "category": cs.skill.category,
                    "evidence_context": cs.evidence_context
                }
                for cs in profile.skills
            ],
            "educations": [
                {"degree_level": edu.degree_level, "degree": edu.degree}
                for edu in profile.educations
            ],
            "projects": [
                {"title": p.title, "description": p.description, "technologies_used": p.technologies_used}
                for p in profile.projects
            ],
            "experiences": [
                {"job_title": exp.job_title, "company": exp.company}
                for exp in profile.experiences
            ]
        }

        all_jobs = await job_repo.list_all(db, limit=100)
        jobs_pool = []
        for job in all_jobs:
            req_skills = [{"canonical_name": r.skill.canonical_name} for r in job.requirements if r.is_required]
            pref_skills = [{"canonical_name": r.skill.canonical_name} for r in job.requirements if not r.is_required]
            jobs_pool.append({
                "id": job.id,
                "title": job.title,
                "company": job.company,
                "raw_text": job.raw_description,
                "min_years_experience": job.min_years_experience,
                "min_education_level": job.min_education_level,
                "required_skills": req_skills,
                "preferred_skills": pref_skills
            })

        return job_recommender.recommend_jobs(cand_dict, jobs_pool, top_k=top_k)


recommendation_service = RecommendationService()
