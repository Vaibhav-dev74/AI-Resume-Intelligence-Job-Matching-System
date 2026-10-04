from typing import Dict, Any
from app.ai.extraction.contact_extractor import contact_extractor
from app.ai.extraction.education_extractor import education_extractor
from app.ai.extraction.experience_extractor import experience_extractor
from app.ai.extraction.skill_extractor import skill_extractor
from app.ai.extraction.project_extractor import project_extractor


class ResumeExtractor:
    @classmethod
    def extract_profile(cls, raw_text: str, sections: Dict[str, str]) -> Dict[str, Any]:
        header_text = sections.get("header", "")
        summary_text = sections.get("summary", "")
        exp_text = sections.get("experience", "")
        edu_text = sections.get("education", "")
        skills_text = sections.get("skills", "")
        proj_text = sections.get("projects", "")

        contacts = contact_extractor.extract(raw_text, header_text)
        experiences, total_years = experience_extractor.extract(exp_text, raw_text)
        educations = education_extractor.extract(edu_text, raw_text)

        skills_combined_text = f"{skills_text}\n{exp_text}\n{proj_text}".strip()
        skills = skill_extractor.extract_skills(skills_combined_text or raw_text)
        categorized_skills = skill_extractor.categorize_skills(skills)

        projects = project_extractor.extract(proj_text, "")
        inferred_role = cls._infer_role(experiences, skills)
        summary = summary_text or (experiences[0]["description"][:300] if experiences else None)

        return {
            "full_name": contacts.get("name") or "Candidate",
            "email": contacts.get("email"),
            "phone": contacts.get("phone"),
            "location": None,
            "linkedin_url": contacts.get("linkedin"),
            "github_url": contacts.get("github"),
            "portfolio_url": None,
            "summary": summary,
            "total_years_experience": total_years,
            "inferred_primary_role": inferred_role,
            "skills": skills,
            "categorized_skills": categorized_skills,
            "experiences": experiences,
            "educations": educations,
            "projects": projects,
            "certifications": []
        }

    @classmethod
    def _infer_role(cls, experiences: list, skills: list) -> str:
        if experiences and experiences[0].get("job_title"):
            return experiences[0]["job_title"]

        skill_names = {s["canonical_name"].lower() for s in skills}
        ai_ml_count = len(skill_names.intersection({"pytorch", "tensorflow", "machine learning", "deep learning", "nlp", "computer vision"}))
        backend_count = len(skill_names.intersection({"fastapi", "flask", "django", "postgresql", "sql", "docker", "rest apis"}))
        frontend_count = len(skill_names.intersection({"react", "typescript", "javascript", "next.js"}))

        if ai_ml_count >= 2:
            return "Machine Learning / AI Engineer"
        elif backend_count >= 2:
            return "Backend Software Engineer"
        elif frontend_count >= 2:
            return "Frontend Web Developer"
        return "Software Engineer"


resume_extractor = ResumeExtractor()
