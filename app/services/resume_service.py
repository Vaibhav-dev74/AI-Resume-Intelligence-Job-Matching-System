import os
import uuid
from typing import Dict, Any, List
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.config import settings
from app.core.security import validate_file_safety, sanitize_filename, anonymize_text
from app.core.logging import logger
from app.models.resume import Resume
from app.models.candidate import CandidateProfile, CandidateSkill, Experience, Education, Project
from app.document_processing.parser_factory import document_parser_factory
from app.ai.extraction.resume_extractor import resume_extractor
from app.ai.embeddings.embedding_engine import embedding_engine
from app.repositories.resume_repo import resume_repo
from app.repositories.skill_repo import skill_repo


class ResumeService:
    @classmethod
    async def process_and_save_resume(
        cls,
        db: AsyncSession,
        file_bytes: bytes,
        filename: str,
        user_id: str = None
    ) -> Resume:
        is_safe, msg = validate_file_safety(file_bytes, filename)
        if not is_safe:
            raise ValueError(msg)

        clean_name = sanitize_filename(filename)
        resume_id = str(uuid.uuid4())
        save_path = os.path.join(str(settings.STORAGE_DIR), f"{resume_id}_{clean_name}")

        with open(save_path, "wb") as f:
            f.write(file_bytes)

        try:
            raw_text, sections, page_count = document_parser_factory.parse_document(file_bytes, clean_name)
        except Exception as e:
            logger.error(f"Failed to parse document {clean_name}: {e}")
            raise ValueError(f"Document parsing failure: {str(e)}")

        anonymized = anonymize_text(raw_text)

        resume_obj = Resume(
            id=resume_id,
            user_id=user_id,
            file_name=clean_name,
            file_path=save_path,
            file_size_bytes=len(file_bytes),
            mime_type="application/pdf" if clean_name.endswith(".pdf") else "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            raw_text=raw_text,
            anonymized_text=anonymized,
            processing_status="PROCESSING"
        )
        await resume_repo.create_resume(db, resume_obj)

        profile_data = resume_extractor.extract_profile(raw_text, sections)
        profile_embedding = embedding_engine.encode(f"{profile_data.get('summary', '')} {' '.join([s['canonical_name'] for s in profile_data.get('skills', [])])}")

        profile_obj = CandidateProfile(
            resume_id=resume_obj.id,
            full_name=profile_data["full_name"],
            email=profile_data["email"],
            phone=profile_data["phone"],
            location=profile_data["location"],
            linkedin_url=profile_data["linkedin_url"],
            github_url=profile_data["github_url"],
            portfolio_url=profile_data["portfolio_url"],
            summary=profile_data["summary"],
            total_years_experience=profile_data["total_years_experience"],
            inferred_primary_role=profile_data["inferred_primary_role"],
            embedding=profile_embedding.tolist()
        )
        db.add(profile_obj)
        await db.flush()

        for sk in profile_data["skills"]:
            skill_entity = await skill_repo.get_or_create(
                db,
                canonical_name=sk["canonical_name"],
                category=sk["category"]
            )
            cand_skill = CandidateSkill(
                profile_id=profile_obj.id,
                skill_id=skill_entity.id,
                raw_extracted_text=sk["raw_extracted_text"],
                evidence_context=sk.get("evidence_context"),
                confidence_score=sk.get("confidence_score", 1.0)
            )
            db.add(cand_skill)

        for exp in profile_data["experiences"]:
            exp_obj = Experience(
                profile_id=profile_obj.id,
                job_title=exp["job_title"],
                company=exp["company"],
                location=exp["location"],
                start_date=exp["start_date"],
                end_date=exp["end_date"],
                is_current=exp["is_current"],
                duration_months=exp["duration_months"],
                description=exp["description"],
                key_achievements=exp["key_achievements"]
            )
            db.add(exp_obj)

        for edu in profile_data["educations"]:
            edu_obj = Education(
                profile_id=profile_obj.id,
                institution=edu["institution"],
                degree=edu["degree"],
                degree_level=edu["degree_level"],
                field_of_study=edu["field_of_study"],
                graduation_year=edu["graduation_year"],
                gpa=edu["gpa"]
            )
            db.add(edu_obj)

        for proj in profile_data["projects"]:
            proj_obj = Project(
                profile_id=profile_obj.id,
                title=proj["title"],
                description=proj["description"],
                technologies_used=proj["technologies_used"],
                repo_url=proj["repo_url"]
            )
            db.add(proj_obj)

        resume_obj.processing_status = "COMPLETED"
        await db.flush()

        full_resume = await resume_repo.get_by_id(db, resume_obj.id)
        return full_resume


resume_service = ResumeService()
