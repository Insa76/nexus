
from unittest.mock import AsyncMock, MagicMock

import pytest

from engine.engine import Engine
from planner.intent_recognizer import IntentRecognizer
from runtime.runtime import Runtime


def build_engine() -> Engine:
    runtime = MagicMock(spec=Runtime)
    runtime.tool_registry = MagicMock()
    runtime.tool_registry.describe.return_value = []
    runtime.tool_registry.resolve = MagicMock()
    recognizer = IntentRecognizer()
    intent_provider = MagicMock()
    intent_provider.recognize = AsyncMock(
        side_effect=lambda text, _capabilities, context: recognizer.recognize(
            text, context
        )
    )
    return Engine(runtime=runtime, intent_provider=intent_provider)


@pytest.mark.asyncio
async def test_engine_remembers_and_recalls_a_fact() -> None:
    engine = build_engine()
    stored = await engine.execute(
        "Recordá que mi proyecto actual se llama NEXUS."
    )
    recalled = await engine.execute(
        "¿Cómo se llama mi proyecto actual?"
    )

    assert stored.success
    assert "NEXUS" in stored.message
    assert recalled.success
    assert "NEXUS" in recalled.message
    assert engine.semantic_memory.get_value("user", "proyecto actual") == "NEXUS"


@pytest.mark.asyncio
async def test_engine_executes_compound_remember_and_recall() -> None:
    engine = build_engine()
    result = await engine.execute(
        "Recordá que mi proyecto actual se llama NEXUS y después "
        "decime qué nombre te pedí recordar"
    )

    assert result.success
    assert "NEXUS" in result.message
    assert engine.semantic_memory.get_value("user", "proyecto actual") == "NEXUS"



def test_invalid_compound_memory_intent_does_not_write_partial_fact() -> None:
    engine = build_engine()

    recognizer = IntentRecognizer()
    intent = recognizer.recognize(
        "Recordá que mi proyecto actual se llama NEXUS y después "
        "decime qué nombre te pedí recordar"
    )

    assert intent.sub_intents
    intent.sub_intents[-1].action = "system.recall_fact"
    intent.sub_intents[-1].parameters = {
        "subject": "user",
        "predicate": "",
    }

    result = engine._handle_semantic_memory_intent(intent, "prueba")

    assert result is None
    assert engine.semantic_memory.get_value("user", "proyecto actual") is None


@pytest.mark.asyncio
async def test_engine_recalls_all_user_facts() -> None:
    engine = build_engine()

    await engine.execute(
        "Recordá que mi proyecto actual se llama NEXUS."
    )
    await engine.execute(
        "Recordá que mi prueba de persistencia es octubre 2026."
    )

    result = await engine.execute("¿Qué recordás sobre mí?")

    assert result.success
    assert "NEXUS" in result.message
    assert "octubre 2026" in result.message
    assert "proyecto actual" in result.message
    assert "prueba de persistencia" in result.message


