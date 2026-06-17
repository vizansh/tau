from collections.abc import AsyncIterator, Mapping
from json import loads

import httpx
import pytest

from tau_agent import AgentTool, AgentToolResult, ToolCall, UserMessage
from tau_agent.types import JSONValue
from tau_ai import (
    FakeProvider,
    OpenAICompatibleConfig,
    OpenAICompatibleProvider,
    ProviderResponseEndEvent,
    ProviderResponseStartEvent,
    ProviderTextDeltaEvent,
    ProviderToolCallEvent,
    openai_compatible_config_from_env,
)


async def _collect(stream: AsyncIterator[object]) -> list[object]:
    return [event async for event in stream]


@pytest.mark.anyio
async def test_fake_provider_replays_scripted_events() -> None:
    scripted = [
        ProviderResponseStartEvent(model="fake-model"),
        ProviderTextDeltaEvent(delta="hello"),
        ProviderResponseEndEvent(message={"role": "assistant", "content": "hello"}),
    ]
    provider = FakeProvider([scripted])

    events = await _collect(
        provider.stream_response(
            model="fake-model",
            system="system prompt",
            messages=[UserMessage(content="hi")],
            tools=[],
        )
    )

    assert events == scripted
    assert provider.calls[0][0] == "fake-model"
    assert provider.calls[0][1] == "system prompt"


def test_openai_compatible_config_from_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    monkeypatch.setenv("OPENAI_BASE_URL", "https://example.test/v1/")
    monkeypatch.setenv("OPENAI_TIMEOUT_SECONDS", "12.5")

    config = openai_compatible_config_from_env()

    assert config.api_key == "test-key"
    assert config.base_url == "https://example.test/v1"
    assert config.timeout_seconds == 12.5


def test_openai_compatible_config_from_env_rejects_invalid_timeout(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    monkeypatch.setenv("OPENAI_TIMEOUT_SECONDS", "0")

    with pytest.raises(RuntimeError, match="greater than 0"):
        openai_compatible_config_from_env()


@pytest.mark.anyio
async def test_openai_compatible_provider_uses_configured_timeout() -> None:
    provider = OpenAICompatibleProvider(
        OpenAICompatibleConfig(
            api_key="test-key",
            base_url="https://example.test/v1",
            timeout_seconds=7.5,
        )
    )
    try:
        client = provider._get_client()

        assert client.timeout.connect == 7.5
        assert client.timeout.read == 7.5
    finally:
        await provider.aclose()


@pytest.mark.anyio
async def test_openai_compatible_provider_formats_request_and_streams_text() -> None:
    requests: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        return httpx.Response(
            200,
            text=(
                'data: {"choices":[{"delta":{"content":"Hel"}}]}\n\n'
                'data: {"choices":[{"delta":{"content":"lo"},"finish_reason":"stop"}]}\n\n'
                "data: [DONE]\n\n"
            ),
            headers={"content-type": "text/event-stream"},
        )

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
        provider = OpenAICompatibleProvider(
            OpenAICompatibleConfig(api_key="test-key", base_url="https://example.test/v1"),
            client=client,
        )

        events = await _collect(
            provider.stream_response(
                model="test-model",
                system="You are Tau.",
                messages=[UserMessage(content="Say hello")],
                tools=[],
            )
        )

    assert [event.type for event in events] == [
        "response_start",
        "text_delta",
        "text_delta",
        "response_end",
    ]
    assert isinstance(events[-1], ProviderResponseEndEvent)
    assert events[-1].message.content == "Hello"
    assert events[-1].finish_reason == "stop"

    request = requests[0]
    assert request.url == "https://example.test/v1/chat/completions"
    assert request.headers["authorization"] == "Bearer test-key"

    payload = loads(request.content)
    assert payload["model"] == "test-model"
    assert payload["stream"] is True
    assert payload["messages"] == [
        {"role": "system", "content": "You are Tau."},
        {"role": "user", "content": "Say hello"},
    ]


@pytest.mark.anyio
async def test_openai_compatible_provider_streams_tool_calls() -> None:
    async def executor(arguments: Mapping[str, JSONValue]) -> AgentToolResult:
        return AgentToolResult(
            tool_call_id="call-1",
            name="read",
            ok=True,
            content=str(arguments),
        )

    tool = AgentTool(
        name="read",
        description="Read a file.",
        input_schema={"type": "object", "properties": {"path": {"type": "string"}}},
        executor=executor,
    )

    def handler(request: httpx.Request) -> httpx.Response:
        payload = loads(request.content)
        assert payload["tools"] == [
            {
                "type": "function",
                "function": {
                    "name": "read",
                    "description": "Read a file.",
                    "parameters": {"type": "object", "properties": {"path": {"type": "string"}}},
                },
            }
        ]
        return httpx.Response(
            200,
            text=(
                'data: {"choices":[{"delta":{"tool_calls":[{"index":0,"id":"call-1",'
                '"function":{"name":"read","arguments":"{\\"path\\":"}}]}}]}\n\n'
                'data: {"choices":[{"delta":{"tool_calls":[{"index":0,'
                '"function":{"arguments":"\\"README.md\\"}"}}]},"finish_reason":"tool_calls"}]}\n\n'
                "data: [DONE]\n\n"
            ),
            headers={"content-type": "text/event-stream"},
        )

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
        provider = OpenAICompatibleProvider(
            OpenAICompatibleConfig(api_key="test-key", base_url="https://example.test/v1"),
            client=client,
        )

        events = await _collect(
            provider.stream_response(
                model="test-model",
                system="You are Tau.",
                messages=[UserMessage(content="Read README.md")],
                tools=[tool],
            )
        )

    tool_call_events = [event for event in events if isinstance(event, ProviderToolCallEvent)]

    assert tool_call_events == [
        ProviderToolCallEvent(
            tool_call=ToolCall(id="call-1", name="read", arguments={"path": "README.md"})
        )
    ]
    assert isinstance(events[-1], ProviderResponseEndEvent)
    assert events[-1].message.tool_calls == [
        ToolCall(id="call-1", name="read", arguments={"path": "README.md"})
    ]
    assert events[-1].finish_reason == "tool_calls"
