from pathlib import Path

import pytest

from tau_coding.paths import TauPaths
from tau_coding.provider_config import (
    DEFAULT_MODEL,
    OpenAICompatibleProviderConfig,
    ProviderConfigError,
    ProviderSettings,
    load_provider_settings,
    openai_compatible_config_from_provider,
    provider_settings_from_json,
    resolve_provider_selection,
    save_provider_settings,
    upsert_openai_compatible_provider,
)


def test_load_provider_settings_missing_file_uses_openai_default(tmp_path: Path) -> None:
    settings = load_provider_settings(TauPaths(home=tmp_path / ".tau"))

    assert settings.default_provider == "openai"
    assert [provider.name for provider in settings.providers] == ["openai"]
    assert settings.providers[0].default_model == DEFAULT_MODEL


def test_save_and_load_provider_settings_round_trip(tmp_path: Path) -> None:
    paths = TauPaths(home=tmp_path / ".tau")
    settings = ProviderSettings(
        default_provider="local",
        providers=(
            OpenAICompatibleProviderConfig(
                name="local",
                base_url="http://localhost:11434/v1",
                api_key_env="LOCAL_API_KEY",
                models=("qwen", "llama"),
                default_model="qwen",
                timeout_seconds=120,
            ),
        ),
    )

    path = save_provider_settings(settings, paths)
    loaded = load_provider_settings(paths)

    assert path == tmp_path / ".tau" / "providers.json"
    assert loaded == settings


def test_upsert_openai_compatible_provider_replaces_and_sets_default() -> None:
    settings = ProviderSettings()
    provider = OpenAICompatibleProviderConfig(
        name="local",
        base_url="http://localhost:11434/v1",
        api_key_env="LOCAL_API_KEY",
        models=("qwen",),
        default_model="qwen",
    )

    updated = upsert_openai_compatible_provider(settings, provider, set_default=True)
    replaced = upsert_openai_compatible_provider(
        updated,
        OpenAICompatibleProviderConfig(
            name="local",
            base_url="http://localhost:11434/v1",
            api_key_env="LOCAL_API_KEY",
            models=("llama",),
            default_model="llama",
        ),
        set_default=True,
    )

    assert updated.default_provider == "local"
    assert [item.name for item in updated.providers] == ["local", "openai"]
    assert replaced.get_provider("local").default_model == "llama"


def test_resolve_provider_selection_uses_configured_defaults() -> None:
    settings = ProviderSettings(
        default_provider="local",
        providers=(
            OpenAICompatibleProviderConfig(
                name="local",
                base_url="http://localhost:11434/v1",
                api_key_env="LOCAL_API_KEY",
                models=("qwen",),
                default_model="qwen",
            ),
        ),
    )

    selection = resolve_provider_selection(settings)

    assert selection.provider.name == "local"
    assert selection.model == "qwen"


def test_resolve_provider_selection_rejects_unknown_provider() -> None:
    with pytest.raises(ProviderConfigError, match="Unknown provider"):
        resolve_provider_selection(ProviderSettings(), provider_name="missing")


def test_openai_compatible_config_from_provider_uses_configured_env_var(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("LOCAL_API_KEY", "test-key")
    provider = OpenAICompatibleProviderConfig(
        name="local",
        base_url="http://localhost:11434/v1/",
        api_key_env="LOCAL_API_KEY",
        models=("qwen",),
        default_model="qwen",
    )

    config = openai_compatible_config_from_provider(provider)

    assert config.api_key == "test-key"
    assert config.base_url == "http://localhost:11434/v1"
    assert config.timeout_seconds == 60.0


def test_openai_compatible_config_from_provider_uses_configured_timeout(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("LOCAL_API_KEY", "test-key")
    provider = OpenAICompatibleProviderConfig(
        name="local",
        base_url="http://localhost:11434/v1/",
        api_key_env="LOCAL_API_KEY",
        models=("qwen",),
        default_model="qwen",
        timeout_seconds=180,
    )

    config = openai_compatible_config_from_provider(provider)

    assert config.timeout_seconds == 180


def test_provider_settings_from_json_rejects_invalid_timeout() -> None:
    with pytest.raises(ProviderConfigError, match="greater than 0"):
        provider_settings_from_json(
            {
                "default_provider": "local",
                "providers": [
                    {
                        "type": "openai-compatible",
                        "name": "local",
                        "base_url": "http://localhost:11434/v1",
                        "api_key_env": "LOCAL_API_KEY",
                        "models": ["qwen"],
                        "default_model": "qwen",
                        "timeout_seconds": 0,
                    }
                ],
            }
        )


def test_openai_compatible_provider_config_rejects_invalid_timeout() -> None:
    with pytest.raises(ProviderConfigError, match="greater than 0"):
        OpenAICompatibleProviderConfig(name="local", timeout_seconds=0)
