
import asyncio

from planner import ollama_intent_provider
from planner.ollama_intent_provider import OllamaIntentProvider


def test_recognize_returns_unknown_when_ollama_times_out(
    monkeypatch,
) -> None:
    class SlowClient:
        def __init__(self, **kwargs) -> None:
            pass

        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc_value, traceback):
            return False

        async def chat(self, **kwargs):
            await asyncio.sleep(1)

    monkeypatch.setattr(
        ollama_intent_provider,
        "AsyncClient",
        SlowClient,
    )

    provider = OllamaIntentProvider()
    provider.REQUEST_TIMEOUT_SECONDS = 0.01

    intent = asyncio.run(
        provider.recognize("solicitud de prueba sin respuesta")
    )

    assert intent.action == "system.unknown"
