from __future__ import annotations

from security.assignment_store import AssignmentStore
from security.models import Actor
from security.permissions import Permission


class AuthorizationService:
    """
    Evalúa los permisos efectivos de un actor mediante sus roles.

    Política: denegación por defecto.
    Consulta las asignaciones actuales en cada autorización.
    """

    def __init__(self, assignment_store: AssignmentStore) -> None:
        self._assignment_store = assignment_store

    def is_allowed(
        self,
        actor: Actor,
        permission: Permission,
    ) -> bool:
        for assignment in self._assignment_store.list():
            assigned_actor = assignment.actor

            same_identity = (
                assigned_actor.id == actor.id
                and assigned_actor.actor_type == actor.actor_type
            )

            if (
                same_identity
                and assignment.role.has_permission(permission)
            ):
                return True

        return False
