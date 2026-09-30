from fastapi import APIRouter
from app.api.v1.resumes import router as resumes_router
from app.api.v1.jobs import router as jobs_router
from app.api.v1.matches import router as matches_router
from app.api.v1.evaluations import router as evaluations_router
from app.api.v1.skills import router as skills_router

api_v1_router = APIRouter()
api_v1_router.include_router(resumes_router)
api_v1_router.include_router(jobs_router)
api_v1_router.include_router(matches_router)
api_v1_router.include_router(evaluations_router)
api_v1_router.include_router(skills_router)
