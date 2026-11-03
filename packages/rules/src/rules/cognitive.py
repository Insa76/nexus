from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from rules.capability import RuleCapability
from rules.models import Rule, RuleStatus


@dataclass(frozen=True, slots=True)
class RuleCognitiveResult:
    rules: tuple[Rule, ...]
    metadata: dict[str, Any]


class RuleCognitiveAccess:
    """Traduce operaciones cognitivas al subsistema Rules."""

    def __init__(self, capability: RuleCapability) -> None:
        self._capability = capability

    def find_relevant(self, *, context: object) -> RuleCognitiveResult:
        rules = self._capability.relevant(context=context)
        return RuleCognitiveResult(
            rules=tuple(rules),
            metadata={"operation": "rules.find_relevant", "count": len(rules)},
        )

    def get(self, rule_id: str, *, context: object) -> Rule | None:
        return self._capability.get_for_context(rule_id, context=context)

    def list(self, *, context: object) -> tuple[Rule, ...]:
        return tuple(self._capability.relevant(context=context))

    def create(self, *, context: object, name: str, description: str | None = None) -> Rule:
        return self._capability.create_for_context(name=name, description=description, context=context)

    def update(self, rule_id: str, *, context: object,
               name: str | None = None, description: str | None = None) -> Rule | None:
        return self._capability.update_for_context(
            rule_id, context=context, name=name, description=description,
        )

    def set_status(self, rule_id: str, target_status: RuleStatus,
                   *, context: object) -> Rule | None:
        return self._capability.set_status_for_context(
            rule_id, target_status, context=context,
        )
