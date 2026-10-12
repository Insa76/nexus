from __future__ import annotations

from dataclasses import dataclass

from security.assignment_store import AssignmentStore
from security.assignments import ActorRoleAssignment


@dataclass(slots=True)
class AssignmentCapability:
    """Gestiona las asignaciones de roles a actores."""

    store: AssignmentStore

    def assign(self, assignment: ActorRoleAssignment) -> None:
        self.store.add(assignment)

    def list(self) -> tuple[ActorRoleAssignment, ...]:
        return self.store.list()

    def revoke(self, assignment: ActorRoleAssignment) -> bool:
        return self.store.remove(assignment)
