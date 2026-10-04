from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.core.config import settings
from app.core.logging import logger
from app.models.database import init_db
from app.api.v1.router import api_v1_router
from app.api.rest_api import router as rest_api_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Initializing AI Resume Intelligence Platform...")
    await init_db()
    logger.info("System startup complete. Ready to receive requests.")
    yield
    logger.info("System shutting down...")


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Production-grade explainable AI platform for resume parsing, skill normalization, semantic matching, gap analysis, and job recommendations.",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(ValueError)
async def value_error_handler(request: Request, exc: ValueError):
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"error": "Bad Request", "detail": str(exc)}
    )


@app.get("/health", tags=["System"])
async def health_check():
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "model_provider": settings.MODEL_PROVIDER
    }


@app.get("/", tags=["System"])
async def root():
    return {
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "documentation": "/docs",
        "health": "/health",
        "api_v1_prefix": settings.API_V1_PREFIX
    }


app.include_router(api_v1_router, prefix=settings.API_V1_PREFIX)
app.include_router(rest_api_router, prefix="/api")
