from __future__ import annotations

from rules.models import Rule


class RuleStore:
    """In-memory store for assistant rules."""

    def __init__(self) -> None:
        self._rules: dict[str, Rule] = {}

    def add(self, rule: Rule) -> Rule:
        self._rules[rule.id] = rule
        return rule

    def get(self, rule_id: str) -> Rule | None:
        return self._rules.get(rule_id)

    def list(self) -> list[Rule]:
        return list(self._rules.values())

    def update(self, rule: Rule) -> Rule:
        if rule.id not in self._rules:
            raise KeyError(
                f"Rule not found: {rule.id}"
            )

        self._rules[rule.id] = rule
        return rule

    def remove(self, rule_id: str) -> Rule | None:
        return self._rules.pop(rule_id, None)

    def clear(self) -> None:
        self._rules.clear()

    def count(self) -> int:
        return len(self._rules)
