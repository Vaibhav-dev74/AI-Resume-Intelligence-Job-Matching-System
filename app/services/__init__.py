from app.services.resume_service import resume_service, ResumeService
from app.services.job_service import job_service, JobService
from app.services.matching_service import matching_service, MatchingService
from app.services.recommendation_service import recommendation_service, RecommendationService
from app.services.evaluation_service import evaluation_service, EvaluationService

__all__ = [
    "resume_service", "ResumeService",
    "job_service", "JobService",
    "matching_service", "MatchingService",
    "recommendation_service", "RecommendationService",
    "evaluation_service", "EvaluationService",
]
