from __future__ import annotations

from typing import Any

from planner.intent import Intent
from planner.intent_recognizer import IntentRecognizer
from planner.intent_provider import IntentProvider


class RuleIntentProvider(IntentProvider):
    """
    IntentProvider basado en reglas.
    """

    def __init__(
        self,
        recognizer: IntentRecognizer | None = None,
    ) -> None:

        self._recognizer = (
            recognizer
            or IntentRecognizer()
        )

    async def recognize(
        self,
        text: str,
        capabilities: list[dict[str, Any]] | None = None,
        context: dict[str, Any] | None = None,
    ) -> Intent:

        return self._recognizer.recognize(
            text,
            context,
        )
