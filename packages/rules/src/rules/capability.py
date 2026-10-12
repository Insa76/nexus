from __future__ import annotations

from dataclasses import dataclass

from context import AssistantContext

from rules.models import Rule
from rules.resolver import RuleResolver
from rules.store import RuleStore


@dataclass(slots=True)
class RuleCapability:
    """
    Interfaz de acceso a reglas para el Assistant/Cognitive Core.

    Oculta stores y detalles internos del subsistema Rules.
    """

    store: RuleStore
    resolver: RuleResolver

    def create(
        self,
        *,
        name: str,
        description: str | None = None,
        user_id: str | None = None,
        organization_id: str | None = None,
        project_id: str | None = None,
    ) -> Rule:
        rule = Rule.create(
            name=name,
            description=description,
            user_id=user_id,
            organization_id=organization_id,
            project_id=project_id,
        )

        return self.store.add(rule)

    def get(
        self,
        rule_id: str,
    ) -> Rule | None:
        return self.store.get(rule_id)

    def list(
        self,
    ) -> list[Rule]:
        return self.store.list()

    def relevant(
        self,
        *,
        context: AssistantContext,
    ) -> list[Rule]:
        return self.resolver.resolve(context)

    def update(
        self,
        rule: Rule,
    ) -> Rule:
        return self.store.update(rule)

    def remove(
        self,
        rule_id: str,
    ) -> Rule | None:
        return self.store.remove(rule_id)
