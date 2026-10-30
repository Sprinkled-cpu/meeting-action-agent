"""
Configuration management for AI Meeting-to-Action Agent.
Supports environment variables, .env files, and runtime overrides.
"""

import os
from functools import lru_cache
from typing import Optional, Literal
from pydantic import BaseModel, Field


class Settings(BaseModel):
    app_name: str = "AI Meeting-to-Action Agent"
    app_version: str = "1.0.0"
    app_env: Literal["development", "production", "testing"] = Field(
        default_factory=lambda: os.getenv("APP_ENV", "development")  # type: ignore
    )
    log_level: str = Field(default_factory=lambda: os.getenv("LOG_LEVEL", "INFO"))
    
    # LLM Provider Configuration
    default_provider: Literal["mock", "openai", "gemini"] = Field(
        default_factory=lambda: os.getenv("DEFAULT_LLM_PROVIDER", "mock")  # type: ignore
    )
    openai_api_key: Optional[str] = Field(default_factory=lambda: os.getenv("OPENAI_API_KEY"))
    openai_model: str = Field(default_factory=lambda: os.getenv("OPENAI_MODEL", "gpt-4o"))
    gemini_api_key: Optional[str] = Field(default_factory=lambda: os.getenv("GEMINI_API_KEY"))
    gemini_model: str = Field(default_factory=lambda: os.getenv("GEMINI_MODEL", "gemini-2.0-flash"))
    
    # Execution & Audit controls
    enable_contradiction_audit: bool = True
    enable_ownership_audit: bool = True
    enable_scope_creep_audit: bool = True
    strict_validation: bool = True
    request_timeout_seconds: int = 45
    max_retries: int = 3
    
    # API Server configuration
    api_host: str = Field(default_factory=lambda: os.getenv("API_HOST", "0.0.0.0"))
    api_port: int = Field(default_factory=lambda: int(os.getenv("API_PORT", "8000")))
    cors_origins: list[str] = ["*"]


@lru_cache()
def get_settings() -> Settings:
    """Cached singleton instance of application settings."""
    return Settings()
