from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class FailureCase(BaseModel):
    sample_id: str
    component: str
    input_snippet: str
    ground_truth: Any
    prediction: Any
    error_analysis: str


class EvaluationMetrics(BaseModel):
    skill_extraction_precision: float
    skill_extraction_recall: float
    skill_extraction_f1: float
    job_requirement_accuracy: float
    semantic_similarity_mrr: float
    avg_inference_latency_ms: float
    total_eval_samples: int
    failure_cases: List[FailureCase] = Field(default_factory=list)


class EvaluationRunResponse(BaseModel):
    run_id: str
    timestamp: str
    metrics: EvaluationMetrics
    summary: str
