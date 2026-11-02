from __future__ import annotations

import pytest

from planner.hybrid_intent_provider import HybridIntentProvider
from planner.intent import Intent
from planner.intent_recognizer import IntentRecognizer
from planner.rule_intent_provider import RuleIntentProvider


class OllamaMustNotBeCalled:
    async def recognize(self, text, capabilities=None, context=None) -> Intent:
        raise AssertionError("Ollama no debe invocarse si las reglas reconocen la solicitud completa")


@pytest.mark.asyncio
async def test_hybrid_keeps_deterministic_intent_for_date_and_time_phrase() -> None:
    provider = HybridIntentProvider(
        rule_provider=RuleIntentProvider(IntentRecognizer()),
        ollama_provider=OllamaMustNotBeCalled(),  # type: ignore[arg-type]
    )

    intent = await provider.recognize("Decime la fecha y hora actual del sistema.")

    assert intent.action == "system.get_time"
    assert intent.confidence == 1.0


@pytest.mark.asyncio
async def test_hybrid_still_splits_recognized_compound_actions() -> None:
    provider = HybridIntentProvider(
        rule_provider=RuleIntentProvider(IntentRecognizer()),
        ollama_provider=OllamaMustNotBeCalled(),  # type: ignore[arg-type]
    )

    intent = await provider.recognize("Decime qué hora es y decime qué hora tenemos")

    assert intent.action == "system.get_time"
    assert len(intent.sub_intents) == 2
