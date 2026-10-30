"""
FastAPI Application Entry Point.
Provides Swagger / OpenAPI documentation, CORS middleware, and lifecycle management.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from meeting_action_agent.config import get_settings
from meeting_action_agent.api.routes import health, analyze, export
from meeting_action_agent.logging_config import setup_logging

settings = get_settings()
setup_logging(level=settings.log_level)

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description=(
        "Production-grade Enterprise AI Meeting-to-Action Agent API. "
        "Transforms unstructured transcripts into structured decisions, tasks, questions, follow-ups, "
        "and performs real-time discourse contradiction and alignment audits."
    ),
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS middleware for frontend integrations
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include route modules
app.include_router(health.router)
app.include_router(analyze.router)
app.include_router(export.router)


@app.get("/", include_in_schema=False)
def root_redirect():
    return {
        "service": settings.app_name,
        "version": settings.app_version,
        "docs": "/docs",
        "health": "/health",
    }
