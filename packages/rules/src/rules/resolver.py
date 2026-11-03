from __future__ import annotations

from context import AssistantContext, project_ids_for_context

from rules.models import Rule
from rules.store import RuleStore


class RuleResolver:
    """Resolves rules relevant to an assistant context."""

    def __init__(self, store: RuleStore) -> None:
        self._store = store

    def resolve(
        self,
        context: AssistantContext,
    ) -> list[Rule]:
        rules = self._store.list()

        user = context.user
        organization = context.organization
        project_ids = project_ids_for_context(context)

        resolved: list[Rule] = []

        for rule in rules:
            # Los registros asociados a un proyecto solo son visibles
            # cuando ese proyecto pertenece al alcance activo.
            if rule.project_id is not None:
                if rule.project_id in project_ids:
                    resolved.append(rule)
                continue

            if user is not None and rule.user_id == user.id:
                resolved.append(rule)
                continue

            if (
                organization is not None
                and rule.organization_id == organization.id
            ):
                resolved.append(rule)

        return resolved
