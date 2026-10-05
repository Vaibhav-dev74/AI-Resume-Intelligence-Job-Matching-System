from contextlib import asynccontextmanager
from typing import Any
from fastapi import FastAPI, Request, status, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
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


def _format_http_error(status_code: int, detail: Any) -> JSONResponse:
    code_map = {
        400: "BAD_REQUEST",
        401: "UNAUTHORIZED",
        403: "FORBIDDEN",
        404: "NOT_FOUND",
        413: "PAYLOAD_TOO_LARGE",
        415: "UNSUPPORTED_MEDIA_TYPE",
        422: "UNPROCESSABLE_ENTITY",
        500: "INTERNAL_SERVER_ERROR"
    }
    err_code = code_map.get(status_code, f"HTTP_{status_code}")
    message = detail if isinstance(detail, str) else "HTTP error occurred"
    return JSONResponse(
        status_code=status_code,
        content={
            "success": False,
            "detail": message,
            "error": {
                "code": err_code,
                "message": message,
                "detail": detail
            }
        }
    )


@app.exception_handler(HTTPException)
async def fastapi_http_exception_handler(request: Request, exc: HTTPException):
    return _format_http_error(exc.status_code, exc.detail)


@app.exception_handler(StarletteHTTPException)
async def starlette_http_exception_handler(request: Request, exc: StarletteHTTPException):
    return _format_http_error(exc.status_code, exc.detail)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "success": False,
            "detail": "Request validation failed",
            "error": {
                "code": "VALIDATION_ERROR",
                "message": "Request validation failed",
                "detail": exc.errors()
            }
        }
    )


@app.exception_handler(ValueError)
async def value_error_handler(request: Request, exc: ValueError):
    msg = str(exc)
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "success": False,
            "detail": msg,
            "error": {
                "code": "BAD_REQUEST",
                "message": msg,
                "detail": msg
            }
        }
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception on {request.method} {request.url.path}: {exc}", exc_info=True)
    msg = "An unexpected error occurred while processing the request."
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "success": False,
            "detail": msg,
            "error": {
                "code": "INTERNAL_SERVER_ERROR",
                "message": msg,
                "detail": str(exc) if settings.DEBUG else None
            }
        }
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
