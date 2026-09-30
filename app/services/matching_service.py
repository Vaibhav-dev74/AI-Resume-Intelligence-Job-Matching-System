from typing import Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.match import MatchResult, MatchEvidence
from app.models.resume import Resume
from app.models.job import Job
from app.ai.matching.matcher import matching_engine
from app.ai.matching.gap_analyzer import gap_analyzer
from app.repositories.resume_repo import resume_repo
from app.repositories.job_repo import job_repo
from app.repositories.match_repo import match_repo
from app.repositories.skill_repo import skill_repo
from app.services.job_service import job_service


class MatchingService:
    @classmethod
    async def match_resume_with_job(
        cls,
        db: AsyncSession,
        resume_id: str,
        job_id: Optional[str] = None,
        job_text: Optional[str] = None
    ) -> Dict[str, Any]:
        resume = await resume_repo.get_by_id(db, resume_id)
        if not resume or not resume.profile:
            raise ValueError(f"Resume with id '{resume_id}' not found or has no parsed profile.")

        profile = resume.profile

        if job_id:
            job = await job_repo.get_by_id(db, job_id)
            if not job:
                raise ValueError(f"Job with id '{job_id}' not found.")
        elif job_text:
            job = await job_service.analyze_and_save_job(db, job_text)
        else:
            raise ValueError("Either job_id or job_text must be provided.")

        cand_dict = {
            "full_name": profile.full_name,
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
                {"degree_level": edu.degree_level, "degree": edu.degree, "institution": edu.institution}
                for edu in profile.educations
            ],
            "projects": [
                {"title": p.title, "description": p.description, "technologies_used": p.technologies_used}
                for p in profile.projects
            ],
            "experiences": [
                {"company": exp.company, "job_title": exp.job_title, "duration_months": exp.duration_months}
                for exp in profile.experiences
            ]
        }

        req_skills = []
        pref_skills = []
        for req in job.requirements:
            item = {"canonical_name": req.skill.canonical_name, "category": req.skill.category}
            if req.is_required:
                req_skills.append(item)
            else:
                pref_skills.append(item)

        job_dict = {
            "id": job.id,
            "title": job.title,
            "company": job.company,
            "raw_text": job.raw_description,
            "min_years_experience": job.min_years_experience,
            "min_education_level": job.min_education_level,
            "required_skills": req_skills,
            "preferred_skills": pref_skills
        }

        match_result_data = matching_engine.match(cand_dict, job_dict)
        gap_analysis = gap_analyzer.analyze_gaps(cand_dict["skills"], match_result_data["evidences"])

        match_obj = MatchResult(
            profile_id=profile.id,
            job_id=job.id,
            overall_score=match_result_data["overall_score"],
            required_skill_score=match_result_data["required_skill_score"],
            preferred_skill_score=match_result_data["preferred_skill_score"],
            semantic_score=match_result_data["semantic_score"],
            experience_score=match_result_data["experience_score"],
            project_score=match_result_data["project_score"],
            education_score=match_result_data["education_score"],
            scoring_config_snapshot=match_result_data["scoring_weights"],
            synthesis_explanation=match_result_data["synthesis_explanation"]
        )
        await match_repo.create_match(db, match_obj)

        for ev in match_result_data["evidences"]:
            req_skill_entity = await skill_repo.get_or_create(db, canonical_name=ev["skill_name"], category="tool")
            matched_skill_entity = None
            if ev.get("matched_candidate_skill"):
                matched_skill_entity = await skill_repo.get_or_create(
                    db,
                    canonical_name=ev["matched_candidate_skill"],
                    category="tool"
                )

            ev_obj = MatchEvidence(
                match_id=match_obj.id,
                requirement_skill_id=req_skill_entity.id,
                matched_candidate_skill_id=matched_skill_entity.id if matched_skill_entity else None,
                match_status=ev["match_status"],
                similarity_score=ev["similarity_score"],
                evidence_quote=ev.get("evidence_quote"),
                explanation=ev["explanation"]
            )
            db.add(ev_obj)

        await db.flush()

        return {
            "match_id": match_obj.id,
            "profile_id": profile.id,
            "job_id": job.id,
            "overall_score": match_result_data["overall_score"],
            "scores": {
                "overall_score": match_result_data["overall_score"],
                "required_skill_score": match_result_data["required_skill_score"],
                "preferred_skill_score": match_result_data["preferred_skill_score"],
                "semantic_score": match_result_data["semantic_score"],
                "experience_score": match_result_data["experience_score"],
                "project_score": match_result_data["project_score"],
                "education_score": match_result_data["education_score"],
                "scoring_weights": match_result_data["scoring_weights"]
            },
            "synthesis_explanation": match_result_data["synthesis_explanation"],
            "evidences": match_result_data["evidences"],
            "skill_gap_analysis": gap_analysis,
            "created_at": match_obj.created_at
        }


matching_service = MatchingService()
