from __future__ import annotations

from dataclasses import dataclass, field

from security.assignments import ActorRoleAssignment


@dataclass(slots=True)
class AssignmentStore:
    """Almacena asignaciones de roles durante la ejecución."""

    _assignments: list[ActorRoleAssignment] = field(
        default_factory=list,
        init=False,
        repr=False,
    )

    def add(self, assignment: ActorRoleAssignment) -> None:
        if assignment not in self._assignments:
            self._assignments.append(assignment)

    def list(self) -> tuple[ActorRoleAssignment, ...]:
        return tuple(self._assignments)

    def remove(self, assignment: ActorRoleAssignment) -> bool:
        try:
            self._assignments.remove(assignment)
        except ValueError:
            return False

        return True
