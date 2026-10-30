"""
Provider factory with resilient fallback logic.
"""

from typing import Optional
from meeting_action_agent.providers.base import BaseLLMProvider
from meeting_action_agent.providers.mock_provider import DeterministicOfflineProvider
from meeting_action_agent.providers.openai_provider import OpenAIProvider
from meeting_action_agent.config import get_settings
from meeting_action_agent.logging_config import logger


def get_llm_provider(provider_name: Optional[str] = None) -> BaseLLMProvider:
    """
    Returns an initialized LLM provider based on settings or explicit request.
    Falls back gracefully to DeterministicOfflineProvider if keys are unavailable.
    """
    settings = get_settings()
    chosen = (provider_name or settings.default_provider).lower()

    if chosen == "openai":
        if settings.openai_api_key:
            return OpenAIProvider(
                api_key=settings.openai_api_key, model_name=settings.openai_model
            )
        logger.warning("OpenAI provider requested but OPENAI_API_KEY is not set. Falling back to offline provider.")

    return DeterministicOfflineProvider()
