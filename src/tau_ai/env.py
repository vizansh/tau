"""Environment-based provider configuration helpers."""

from dataclasses import dataclass
from os import environ

DEFAULT_OPENAI_COMPATIBLE_BASE_URL = "https://api.openai.com/v1"
DEFAULT_OPENAI_COMPATIBLE_TIMEOUT_SECONDS = 60.0


@dataclass(frozen=True, slots=True)
class OpenAICompatibleConfig:
    """Configuration for an OpenAI-compatible chat completions endpoint."""

    api_key: str
    base_url: str = DEFAULT_OPENAI_COMPATIBLE_BASE_URL
    timeout_seconds: float = DEFAULT_OPENAI_COMPATIBLE_TIMEOUT_SECONDS


def openai_compatible_config_from_env(
    *,
    api_key_var: str = "OPENAI_API_KEY",
    base_url_var: str = "OPENAI_BASE_URL",
    timeout_seconds_var: str = "OPENAI_TIMEOUT_SECONDS",
    default_timeout_seconds: float = DEFAULT_OPENAI_COMPATIBLE_TIMEOUT_SECONDS,
) -> OpenAICompatibleConfig:
    """Load OpenAI-compatible provider configuration from environment variables."""
    api_key = environ.get(api_key_var)
    if not api_key:
        msg = f"Missing required environment variable: {api_key_var}"
        raise RuntimeError(msg)

    timeout_seconds = _timeout_seconds_from_env(timeout_seconds_var, default_timeout_seconds)
    return OpenAICompatibleConfig(
        api_key=api_key,
        base_url=environ.get(base_url_var, DEFAULT_OPENAI_COMPATIBLE_BASE_URL).rstrip("/"),
        timeout_seconds=timeout_seconds,
    )


def _timeout_seconds_from_env(name: str, default: float) -> float:
    raw = environ.get(name)
    if raw is None:
        return default
    try:
        timeout_seconds = float(raw)
    except ValueError as exc:
        raise RuntimeError(f"Environment variable must be a number: {name}") from exc
    if timeout_seconds <= 0:
        raise RuntimeError(f"Environment variable must be greater than 0: {name}")
    return timeout_seconds
