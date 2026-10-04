import time
import json
from typing import Dict, Any, List, Optional
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, status
from pydantic import BaseModel, Field

from app.core.config import settings
from app.core.presets import PRESET_RESUMES, PRESET_JOBS
from app.document_processing.parser_factory import document_parser_factory
from app.ai.extraction.resume_extractor import resume_extractor
from app.ai.extraction.job_analyzer import job_analyzer
from app.ai.extraction.skill_normalizer import skill_normalizer
from app.ai.matching.matcher import matching_engine
from app.ai.matching.gap_analyzer import gap_analyzer
from app.ai.recommendations.job_recommender import job_recommender
from app.ai.recommendations.resume_improver import resume_improver
from app.services.evaluation_service import evaluation_service

router = APIRouter(tags=["Production REST APIs"])


# ------------------------------------------------------------------------------
# Request & Response Schemas
# ------------------------------------------------------------------------------
class ResumeTextRequest(BaseModel):
    resume_text: str = Field(..., description="Raw textual resume content")
    filename: Optional[str] = Field("resume.txt", description="Document filename")


class JobAnalyzeRequest(BaseModel):
    job_description: str = Field(..., description="Raw job requisition text")
    title: Optional[str] = Field(None, description="Optional job title")
    company: Optional[str] = Field(None, description="Optional company name")


class MatchAnalyzeRequest(BaseModel):
    candidate: Optional[Dict[str, Any]] = Field(None, description="Parsed candidate profile dictionary")
    job: Optional[Dict[str, Any]] = Field(None, description="Parsed job specification dictionary")
    resume_text: Optional[str] = Field(None, description="Fallback raw resume text")
    job_text: Optional[str] = Field(None, description="Fallback raw job text")


class SkillGapsRequest(BaseModel):
    candidate_skills: Optional[List[Any]] = Field(None, description="List of candidate skills")
    evidences: Optional[List[Any]] = Field(None, description="List of match evidence items")
    candidate: Optional[Dict[str, Any]] = Field(None, description="Candidate profile")
    job: Optional[Dict[str, Any]] = Field(None, description="Job specification")


class ResumeImproveRequest(BaseModel):
    candidate: Optional[Dict[str, Any]] = Field(None, description="Parsed candidate profile")
    resume_text: Optional[str] = Field(None, description="Raw resume text")


class RecommendationsRequest(BaseModel):
    candidate: Dict[str, Any] = Field(..., description="Parsed candidate profile")
    jobs: Optional[List[Dict[str, Any]]] = Field(None, description="Optional pool of job requisitions")
    top_k: int = Field(5, description="Number of recommendations to return")


# ------------------------------------------------------------------------------
# Helper Utilities
# ------------------------------------------------------------------------------
def _enrich_evidence_citations(evidences: List[Dict[str, Any]], candidate: Dict[str, Any]):
    for ev in evidences:
        status_val = ev.get("match_status")
        if status_val == "missing":
            ev["citation_source"] = "No supporting evidence found in candidate document"
            continue

        quote = ev.get("evidence_quote") or ""
        if not quote:
            ev["citation_source"] = "Synthesized from candidate profile summary"
            continue

        quote_lower = quote.lower()
        matched_loc = None
        for exp in candidate.get("experiences", []):
            for ach in exp.get("key_achievements", []):
                if quote_lower in ach.lower() or ach.lower() in quote_lower:
                    role = exp.get("job_title", "Role")
                    comp = exp.get("company", "")
                    matched_loc = f"Resume → Professional Experience ({role}{' @ ' + comp if comp else ''})"
                    break
            if matched_loc:
                break

        if not matched_loc:
            for proj in candidate.get("projects", []):
                if quote_lower in proj.get("description", "").lower():
                    matched_loc = f"Resume → Projects ({proj.get('title', 'Project')})"
                    break

        ev["citation_source"] = matched_loc or "Resume → Technical Skills"


# ------------------------------------------------------------------------------
# Endpoints
# ------------------------------------------------------------------------------
@router.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "IntelliResume AI",
        "version": settings.VERSION,
        "model_provider": settings.MODEL_PROVIDER
    }


@router.get("/presets")
async def get_presets():
    """Returns synthetic demo candidate profiles and job descriptions."""
    parsed_resumes = {}
    for name, r_text in PRESET_RESUMES.items():
        c_text, sections, _ = document_parser_factory.parse_document(r_text.encode("utf-8"), f"{name}.txt")
        profile = resume_extractor.extract_profile(c_text, sections)
        parsed_resumes[name] = {
            "name": name,
            "raw_text": r_text,
            "profile": profile
        }

    parsed_jobs = {}
    for name, j_text in PRESET_JOBS.items():
        job_data = job_analyzer.analyze(j_text)
        parsed_jobs[name] = {
            "name": name,
            "raw_text": j_text,
            "job_data": job_data
        }

    return {
        "resumes": parsed_resumes,
        "jobs": parsed_jobs
    }


@router.post("/resume/analyze")
async def analyze_resume(
    file: Optional[UploadFile] = File(None),
    resume_text: Optional[str] = Form(None)
):
    """
    Analyzes a resume via either multipart file upload (.pdf, .docx, .txt)
    or form text.
    """
    try:
        if file is not None:
            file_bytes = await file.read()
            filename = file.filename or "resume.pdf"
            if len(file_bytes) > settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024:
                raise HTTPException(
                    status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                    detail=f"File exceeds maximum allowed size of {settings.MAX_UPLOAD_SIZE_MB}MB."
                )
            cleaned_text, sections, pages = document_parser_factory.parse_document(file_bytes, filename)
        elif resume_text and resume_text.strip():
            filename = "resume.txt"
            cleaned_text, sections, pages = document_parser_factory.parse_document(resume_text.encode("utf-8"), filename)
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Either a file or resume_text must be provided."
            )

        profile = resume_extractor.extract_profile(cleaned_text, sections)
        profile["pages_analyzed"] = pages
        profile["source_filename"] = filename
        return profile
    except HTTPException:
        raise
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ve))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unable to parse document: {str(e)}"
        )


@router.post("/resume/analyze-json")
async def analyze_resume_json(payload: ResumeTextRequest):
    """Analyzes raw resume text provided in a JSON payload."""
    try:
        cleaned_text, sections, pages = document_parser_factory.parse_document(
            payload.resume_text.encode("utf-8"),
            payload.filename or "resume.txt"
        )
        profile = resume_extractor.extract_profile(cleaned_text, sections)
        profile["pages_analyzed"] = pages
        profile["source_filename"] = payload.filename or "resume.txt"
        return profile
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Failed to extract resume: {str(e)}")


@router.post("/job/analyze")
async def analyze_job(payload: JobAnalyzeRequest):
    """Dissects unstructured job requisition text into structured requirements."""
    try:
        if not payload.job_description.strip():
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Job description text cannot be empty.")
        parsed_job = job_analyzer.analyze(
            text=payload.job_description,
            title=payload.title,
            company=payload.company
        )
        return parsed_job
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Failed to analyze job: {str(e)}")


@router.post("/match")
async def match_resume_and_job(payload: MatchAnalyzeRequest):
    """
    Runs the 8-layer explainable matching engine across candidate profile
    and job requirements, returning mathematical breakdown and evidence citations.
    """
    try:
        cand_profile = payload.candidate
        if not cand_profile and payload.resume_text:
            cleaned_text, sections, _ = document_parser_factory.parse_document(
                payload.resume_text.encode("utf-8"),
                "resume.txt"
            )
            cand_profile = resume_extractor.extract_profile(cleaned_text, sections)

        job_data = payload.job
        if not job_data and payload.job_text:
            job_data = job_analyzer.analyze(payload.job_text)

        if not cand_profile or not job_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Both candidate profile (or resume_text) and job specification (or job_text) are required."
            )

        match_result = matching_engine.match(cand_profile, job_data)
        _enrich_evidence_citations(match_result.get("evidences", []), cand_profile)

        # Precompute skill gaps for convenience
        gaps = gap_analyzer.analyze_gaps(cand_profile.get("skills", []), match_result.get("evidences", []))
        match_result["gap_analysis"] = gaps

        weights = match_result.get("scoring_weights", {})
        match_result["breakdown"] = {
            "required_skills": {
                "label": "Required Qualifications",
                "score": match_result["required_skill_score"],
                "weight": weights.get("required_skills", 0.0),
                "contribution": round(match_result["required_skill_score"] * weights.get("required_skills", 0.0), 1)
            },
            "preferred_skills": {
                "label": "Preferred Qualifications",
                "score": match_result["preferred_skill_score"],
                "weight": weights.get("preferred_skills", 0.0),
                "contribution": round(match_result["preferred_skill_score"] * weights.get("preferred_skills", 0.0), 1)
            },
            "semantic_similarity": {
                "label": "Semantic Text Alignment",
                "score": match_result["semantic_score"],
                "weight": weights.get("semantic_similarity", 0.0),
                "contribution": round(match_result["semantic_score"] * weights.get("semantic_similarity", 0.0), 1)
            },
            "experience_duration": {
                "label": "Years of Experience",
                "score": match_result["experience_score"],
                "weight": weights.get("experience_duration", 0.0),
                "contribution": round(match_result["experience_score"] * weights.get("experience_duration", 0.0), 1)
            },
            "project_relevance": {
                "label": "Project Relevance",
                "score": match_result["project_score"],
                "weight": weights.get("project_relevance", 0.0),
                "contribution": round(match_result["project_score"] * weights.get("project_relevance", 0.0), 1)
            },
            "education_level": {
                "label": "Education Level",
                "score": match_result["education_score"],
                "weight": weights.get("education_level", 0.0),
                "contribution": round(match_result["education_score"] * weights.get("education_level", 0.0), 1)
            }
        }
        match_result["evidence_matrix"] = match_result.get("evidences", [])

        return match_result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Compatibility matching failed: {str(e)}"
        )


@router.post("/skill-gaps")
async def get_skill_gaps(payload: SkillGapsRequest):
    """Categorizes missing vs transferable skills and generates 4-week roadmap."""
    try:
        candidate_skills = payload.candidate_skills
        evidences = payload.evidences

        if (candidate_skills is None or evidences is None) and payload.candidate and payload.job:
            candidate_skills = payload.candidate.get("skills", [])
            match_res = matching_engine.match(payload.candidate, payload.job)
            evidences = match_res.get("evidences", [])

        if candidate_skills is None or evidences is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Either (candidate_skills, evidences) or (candidate, job) must be provided."
            )

        gaps = gap_analyzer.analyze_gaps(candidate_skills, evidences)
        gaps["missing_required_skills"] = [s for s in gaps.get("missing_skills", []) if s.get("is_required", True)]
        gaps["learning_roadmap"] = gaps.get("upskilling_roadmap", [])
        return gaps
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Failed to compute skill gaps: {str(e)}")


@router.post("/resume/improve")
async def improve_resume(payload: ResumeImproveRequest):
    """Generates evidence-constrained bullet point enhancements with zero hallucination."""
    try:
        cand_profile = payload.candidate
        if not cand_profile and payload.resume_text:
            cleaned_text, sections, _ = document_parser_factory.parse_document(
                payload.resume_text.encode("utf-8"),
                "resume.txt"
            )
            cand_profile = resume_extractor.extract_profile(cleaned_text, sections)

        if not cand_profile:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Candidate profile or resume text required.")

        result = resume_improver.improve(cand_profile)
        result["strength_index"] = result["strength_score"]
        result["bullet_improvements"] = result["suggestions"]
        result["critique_notes"] = result["formatting_insights"]
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to improve resume: {str(e)}")


@router.post("/recommendations")
async def get_recommendations(payload: RecommendationsRequest):
    """Ranks available job pool for a candidate profile using dense cosine similarity and skill overlap."""
    try:
        jobs_pool = payload.jobs
        if not jobs_pool or len(jobs_pool) < 2:
            # Fall back to default curated preset pool
            jobs_pool = [job_analyzer.analyze(text) for text in PRESET_JOBS.values()]

        recs = job_recommender.recommend_jobs(payload.candidate, jobs_pool, top_k=payload.top_k)
        for r in recs:
            r["fit_score"] = r["overall_fit_score"]
        return recs
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to generate recommendations: {str(e)}")


@router.get("/evaluation")
@router.post("/evaluation/run")
async def get_evaluation_benchmarks():
    """Runs reproducible offline evaluation against the 12 golden test pairs."""
    try:
        result = evaluation_service.run_benchmark()
        if "error" in result:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=result["error"])
        metrics = result.get("metrics", {})
        result["extraction_metrics"] = {
            "precision": metrics.get("skill_extraction_precision", 0.0),
            "recall": metrics.get("skill_extraction_recall", 0.0),
            "overall_f1": metrics.get("skill_extraction_f1", 0.0)
        }
        result["matching_metrics"] = {
            "requirement_accuracy": metrics.get("job_requirement_accuracy", 0.0),
            "semantic_mrr": metrics.get("semantic_similarity_mrr", 0.0),
            "avg_latency_ms": metrics.get("avg_inference_latency_ms", 0.0)
        }
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Benchmark execution failed: {str(e)}")



@router.get("/skills/canonical")
async def get_canonical_skills():
    """Returns the full 36-node skill taxonomy with descriptions, aliases, and transferability edges."""
    try:
        with open(settings.TAXONOMY_PATH, "r", encoding="utf-8") as f:
            tax = json.load(f)
        return tax.get("skills", [])
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to load taxonomy: {str(e)}")
