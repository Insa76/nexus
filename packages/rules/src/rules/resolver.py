from __future__ import annotations

from context import AssistantContext

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
        project_ids = {
            project.id
            for project in context.projects
        }

        resolved: list[Rule] = []

        for rule in rules:
            if user is not None and rule.user_id == user.id:
                resolved.append(rule)
                continue

            if (
                organization is not None
                and rule.organization_id == organization.id
            ):
                resolved.append(rule)
                continue

            if (
                rule.project_id is not None
                and rule.project_id in project_ids
            ):
                resolved.append(rule)

        return resolved
