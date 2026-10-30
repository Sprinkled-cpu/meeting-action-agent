"""
Domain-specific exceptions for Meeting-to-Action Agent.
"""

class MeetingActionAgentError(Exception):
    """Base exception for all agent errors."""
    pass


class TranscriptParseError(MeetingActionAgentError):
    """Raised when transcript format is unparseable or corrupted."""
    pass


class LLMProviderError(MeetingActionAgentError):
    """Raised when upstream LLM API fails or times out."""
    pass


class SchemaValidationError(MeetingActionAgentError):
    """Raised when generated plan violates the strict Pydantic contract."""
    pass


class AuditorError(MeetingActionAgentError):
    """Raised when an internal discourse audit check fails."""
    pass
