import os
from pathlib import Path
from typing import List, Dict, Any
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent.parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    PROJECT_NAME: str = "AI Resume Intelligence & Job Matching Platform"
    VERSION: str = "1.0.0"
    API_V1_PREFIX: str = "/api/v1"
    DEBUG: bool = True

    @field_validator("DEBUG", mode="before")
    @classmethod
    def parse_debug(cls, v):
        if isinstance(v, str):
            return v.lower() in ("true", "1", "yes", "debug")
        return bool(v)

    @field_validator("ALLOWED_ORIGINS", mode="before")
    @classmethod
    def parse_allowed_origins(cls, v):
        if isinstance(v, str):
            if v.startswith("[") and v.endswith("]"):
                import json
                try:
                    return json.loads(v)
                except Exception:
                    pass
            return [x.strip() for x in v.split(",") if x.strip()]
        return v

    HOST: str = "0.0.0.0"
    PORT: int = 8000

    SECRET_KEY: str = "production-ready-secure-key-32-chars-min-xyz123"
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://localhost:4173",
        "http://localhost:8000",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:8000"
    ]
    MAX_UPLOAD_SIZE_MB: int = 10
    ALLOWED_EXTENSIONS: List[str] = [".pdf", ".docx", ".txt"]

    DATABASE_URL: str = "sqlite+aiosqlite:///./resume_intelligence.db"
    DATABASE_URL_SYNC: str = "sqlite:///./resume_intelligence.db"
    USE_PGVECTOR: bool = False

    MODEL_PROVIDER: str = "local"
    EMBEDDING_MODEL_NAME: str = "sentence-transformers/all-MiniLM-L6-v2"
    EMBEDDING_DIMENSION: int = 384
    OPENAI_API_KEY: str = ""
    GEMINI_API_KEY: str = ""

    MATCHING_WEIGHT_REQUIRED_SKILLS: float = 0.40
    MATCHING_WEIGHT_SEMANTIC_SIMILARITY: float = 0.20
    MATCHING_WEIGHT_EXPERIENCE_RELEVANCE: float = 0.15
    MATCHING_WEIGHT_PREFERRED_SKILLS: float = 0.10
    MATCHING_WEIGHT_PROJECT_RELEVANCE: float = 0.10
    MATCHING_WEIGHT_EDUCATION_MATCH: float = 0.05
    TRANSFERABLE_SKILL_PENALTY: float = 0.75
    SEMANTIC_SIMILARITY_THRESHOLD: float = 0.65

    STORAGE_DIR: Path = BASE_DIR / "data" / "storage" / "resumes"
    TAXONOMY_PATH: Path = BASE_DIR / "data" / "taxonomy" / "canonical_skills.json"
    EVAL_DATASET_PATH: Path = BASE_DIR / "data" / "eval" / "benchmark_pairs.json"

    @property
    def matching_weights_dict(self) -> Dict[str, float]:
        return {
            "required_skills": self.MATCHING_WEIGHT_REQUIRED_SKILLS,
            "semantic_similarity": self.MATCHING_WEIGHT_SEMANTIC_SIMILARITY,
            "experience_relevance": self.MATCHING_WEIGHT_EXPERIENCE_RELEVANCE,
            "preferred_skills": self.MATCHING_WEIGHT_PREFERRED_SKILLS,
            "project_relevance": self.MATCHING_WEIGHT_PROJECT_RELEVANCE,
            "education_match": self.MATCHING_WEIGHT_EDUCATION_MATCH,
        }


settings = Settings()

os.makedirs(settings.STORAGE_DIR, exist_ok=True)
os.makedirs(settings.TAXONOMY_PATH.parent, exist_ok=True)
os.makedirs(settings.EVAL_DATASET_PATH.parent, exist_ok=True)
