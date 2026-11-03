from __future__ import annotations

from dataclasses import dataclass, replace

from context import AssistantContext, project_ids_for_context
from rules.models import Rule, RuleStatus
from rules.resolver import RuleResolver
from rules.store import RuleStore


@dataclass(slots=True)
class RuleCapability:
    """Acceso a reglas limitado al contexto operativo activo."""

    store: RuleStore
    resolver: RuleResolver

    @staticmethod
    def _text(value: str, field: str, maximum: int, *, required: bool = True) -> str | None:
        if not isinstance(value, str):
            raise ValueError(f"El campo '{field}' debe ser texto.")
        cleaned = value.strip()
        if required and not cleaned:
            raise ValueError(f"El campo '{field}' es obligatorio.")
        if len(cleaned) > maximum:
            raise ValueError(f"El campo '{field}' supera {maximum} caracteres.")
        return cleaned or None

    def create(self, *, name: str, description: str | None = None,
               user_id: str | None = None, organization_id: str | None = None,
               project_id: str | None = None) -> Rule:
        name = self._text(name, "name", 200)
        description = self._text(description, "description", 4000, required=False)
        return self.store.add(Rule.create(
            name=name, description=description, user_id=user_id,
            organization_id=organization_id, project_id=project_id,
        ))

    def create_for_context(self, *, name: str, context: AssistantContext,
                           description: str | None = None) -> Rule:
        active_project_id = context.metadata.get("active_project_id")
        allowed_projects = project_ids_for_context(context)
        if active_project_id is not None and active_project_id not in allowed_projects:
            raise ValueError("El proyecto activo no pertenece al contexto actual.")
        return self.create(
            name=name, description=description,
            user_id=context.user.id if context.user else None,
            organization_id=context.organization.id if context.organization else None,
            project_id=active_project_id,
        )

    def get(self, rule_id: str) -> Rule | None:
        return self.store.get(rule_id)

    def list(self) -> list[Rule]:
        return self.store.list()

    def relevant(self, *, context: AssistantContext) -> list[Rule]:
        return self.resolver.resolve(context)

    def get_for_context(self, rule_id: str, *, context: AssistantContext) -> Rule | None:
        return next((item for item in self.relevant(context=context) if item.id == rule_id), None)

    def update_for_context(self, rule_id: str, *, context: AssistantContext,
                           name: str | None = None, description: str | None = None) -> Rule | None:
        rule = self.get_for_context(rule_id, context=context)
        if rule is None:
            return None
        changes = {}
        if name is not None:
            changes["name"] = self._text(name, "name", 200)
        if description is not None:
            changes["description"] = self._text(description, "description", 4000, required=False)
        if not changes:
            raise ValueError("No se indicó ningún campo para actualizar.")
        return self.store.update(replace(rule, **changes))

    def set_status_for_context(self, rule_id: str, target: RuleStatus,
                               *, context: AssistantContext) -> Rule | None:
        rule = self.get_for_context(rule_id, context=context)
        if rule is None:
            return None
        return self.store.update(replace(rule, status=target))

    def update(self, rule: Rule) -> Rule:
        return self.store.update(rule)

    def remove(self, rule_id: str) -> Rule | None:
        return self.store.remove(rule_id)
