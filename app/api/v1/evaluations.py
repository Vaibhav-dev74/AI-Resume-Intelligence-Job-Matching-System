from fastapi import APIRouter, HTTPException, status
from app.schemas.evaluation import EvaluationRunResponse
from app.services.evaluation_service import evaluation_service

router = APIRouter(prefix="/evaluations", tags=["Evaluation & Benchmarks"])


@router.get("", response_model=EvaluationRunResponse)
async def run_evaluation_benchmark():
    result = evaluation_service.run_benchmark()
    if "error" in result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=result["error"])
    return result
