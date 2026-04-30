"""Configuration module for AI Content Engine Phase 1.

Loads environment variables, validates required keys, and provides a central
configuration interface for the scraping and synthesis pipeline.
"""

import logging
import os
from typing import Any

from dotenv import load_dotenv

load_dotenv(override=True)

logger = logging.getLogger(__name__)

REQUIRED_KEYS = [
    "YOUTUBE_API_KEY",
    "LLM_PROVIDER",
    "OPENAI_API_KEY",
    "ANTHROPIC_API_KEY",
    "TARGET_NICHE",
    "MAX_TRANSCRIPT_CHARS",
]

OPTIONAL_KEYS = ["OPENAI_COMPATIBLE_API_BASE"]

LLM_PROVIDER_VALUES = ["openai", "anthropic", "openai_compatible"]


class ConfigurationError(Exception):
    """Raised when required environment configuration is missing or invalid."""

    pass


def _get_config_value(key: str) -> str:
    """Retrieve a configuration value from environment variables.

    Args:
        key: The environment variable name to retrieve.

    Returns:
        The value of the environment variable.

    Raises:
        ConfigurationError: If the key is not set or is empty.
    """
    value = os.getenv(key, "")
    if not value:
        raise ConfigurationError(f"Required environment variable '{key}' is not set")
    return value


def validate_config() -> None:
    """Validate that all required configuration keys are present.

    Raises:
        ConfigurationError: If any required key is missing or if LLM_PROVIDER
            is not a valid value.
    """
    missing_keys = [key for key in REQUIRED_KEYS if not os.getenv(key)]
    if missing_keys:
        raise ConfigurationError(
            f"Missing required environment variables: {', '.join(missing_keys)}"
        )

    provider = os.getenv("LLM_PROVIDER", "").strip()
    if provider not in LLM_PROVIDER_VALUES:
        raise ConfigurationError(
            f"LLM_PROVIDER must be one of {LLM_PROVIDER_VALUES}, got '{provider}'"
        )

    if provider == "openai_compatible":
        base_url = os.getenv("OPENAI_COMPATIBLE_API_BASE", "").strip()
        if not base_url:
            raise ConfigurationError(
                "OPENAI_COMPATIBLE_API_BASE is required when LLM_PROVIDER is 'openai_compatible'"
            )


def get_youtube_api_key() -> str:
    """Get the YouTube Data API v3 key.

    Returns:
        The YouTube API key.

    Raises:
        ConfigurationError: If the key is not configured.
    """
    return _get_config_value("YOUTUBE_API_KEY")


def get_llm_provider() -> str:
    """Get the LLM provider ('openai' or 'anthropic').

    Returns:
        The LLM provider name.

    Raises:
        ConfigurationError: If not configured.
    """
    return _get_config_value("LLM_PROVIDER")


def get_openai_api_key() -> str:
    """Get the OpenAI API key.

    Returns:
        The OpenAI API key.

    Raises:
        ConfigurationError: If not configured.
    """
    return _get_config_value("OPENAI_API_KEY")


def get_anthropic_api_key() -> str:
    """Get the Anthropic API key.

    Returns:
        The Anthropic API key.

    Raises:
        ConfigurationError: If not configured.
    """
    return _get_config_value("ANTHROPIC_API_KEY")


def get_target_niche() -> str:
    """Get the target niche for trend scraping.

    Returns:
        The target niche string.

    Raises:
        ConfigurationError: If not configured.
    """
    return _get_config_value("TARGET_NICHE")


def get_max_transcript_chars() -> int:
    """Get the maximum number of transcript characters to send to LLM.

    Returns:
        The max transcript chars as an integer.

    Raises:
        ConfigurationError: If not configured or not a valid integer.
    """
    value = _get_config_value("MAX_TRANSCRIPT_CHARS")
    try:
        return int(value)
    except ValueError:
        raise ConfigurationError(f"MAX_TRANSCRIPT_CHARS must be an integer, got '{value}'")


def get_openaiCompatible_api_base() -> str:
    """Get the base URL for OpenAI-compatible API.

    Returns:
        The base URL string (empty if not using openai_compatible).

    Raises:
        ConfigurationError: If LLM_PROVIDER is 'openai_compatible' but the key is not set.
    """
    provider = os.getenv("LLM_PROVIDER", "")
    if provider != "openai_compatible":
        return ""
    value = os.getenv("OPENAI_COMPATIBLE_API_BASE", "")
    if not value:
        raise ConfigurationError(
            "OPENAI_COMPATIBLE_API_BASE is required when LLM_PROVIDER is 'openai_compatible'"
        )
    return value


def get_openai_model() -> str:
    """Get the OpenAI model name.

    Returns:
        The model name string.
    """
    return os.getenv("OPENAI_MODEL", "gpt-4o-mini")


def get_anthropic_model() -> str:
    """Get the Anthropic model name.

    Returns:
        The model name string.
    """
    return os.getenv("ANTHROPIC_MODEL", "claude-3-haiku-20240307")


class Config:
    """Central configuration object that provides access to all settings.

    This class provides a convenient interface for accessing configuration
    values with validation happening at import time.
    """

    def __init__(self) -> None:
        validate_config()
        self._youtube_api_key = get_youtube_api_key()
        self._llm_provider = get_llm_provider()
        self._openai_api_key = get_openai_api_key()
        self._anthropic_api_key = get_anthropic_api_key()
        self._target_niche = get_target_niche()
        self._max_transcript_chars = get_max_transcript_chars()
        self._openai_compatible_api_base = (
            os.getenv("OPENAI_COMPATIBLE_API_BASE", "")
            if self._llm_provider == "openai_compatible"
            else ""
        )
        self._openai_model = get_openai_model()
        self._anthropic_model = get_anthropic_model()

    @property
    def youtube_api_key(self) -> str:
        return self._youtube_api_key

    @property
    def llm_provider(self) -> str:
        return self._llm_provider

    @property
    def openai_api_key(self) -> str:
        return self._openai_api_key

    @property
    def anthropic_api_key(self) -> str:
        return self._anthropic_api_key

    @property
    def target_niche(self) -> str:
        return self._target_niche

    @property
    def max_transcript_chars(self) -> int:
        return self._max_transcript_chars

    @property
    def openai_compatible_api_base(self) -> str:
        return self._openai_compatible_api_base

    @property
    def openai_model(self) -> str:
        return self._openai_model

    @property
    def anthropic_model(self) -> str:
        return self._anthropic_model


config = Config()