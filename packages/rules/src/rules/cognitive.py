from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from rules.capability import RuleCapability
from rules.models import Rule


@dataclass(frozen=True, slots=True)
class RuleCognitiveResult:
    """
    Resultado de una operación cognitiva sobre Rules.

    Expone información que el Cognitive Core puede utilizar
    sin conocer stores ni detalles internos del subsistema.
    """

    rules: tuple[Rule, ...]
    metadata: dict[str, Any]


class RuleCognitiveAccess:
    """
    Punto de acceso cognitivo a Rules.

    Traduce una necesidad cognitiva del Assistant
    en una operación sobre RuleCapability.
    """

    def __init__(
        self,
        capability: RuleCapability,
    ) -> None:
        self._capability = capability

    def find_relevant(
        self,
        *,
        context: object,
    ) -> RuleCognitiveResult:
        rules = self._capability.relevant(
            context=context,
        )

        return RuleCognitiveResult(
            rules=tuple(rules),
            metadata={
                "operation": "rules.find_relevant",
                "count": len(rules),
            },
        )

    def get(
        self,
        rule_id: str,
        *,
        context: object,
    ) -> Rule | None:
        rules = self._capability.relevant(
            context=context,
        )

        return next(
            (
                rule
                for rule in rules
                if rule.id == rule_id
            ),
            None,
        )

    def list(
        self,
        *,
        context: object,
    ) -> tuple[Rule, ...]:
        return tuple(
            self._capability.relevant(
                context=context,
            )
        )
