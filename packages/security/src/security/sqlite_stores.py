
from __future__ import annotations

from security.assignment_store import AssignmentStore
from security.assignments import ActorRoleAssignment
from security.role_store import RoleStore
from security.roles import Role
from security.sqlite_security_store import SQLiteSecurityStore


class SQLiteRoleStore:
    """Implementa el contrato de RoleStore con persistencia SQLite."""

    def __init__(self, store: SQLiteSecurityStore) -> None:
        self._store = store

    def add(self, role: Role) -> None:
        if self._store.get_role(role.id) is not None:
            raise ValueError(f"Role already exists: {role.id}")

        self._store.save_role(role)

    def get(self, role_id: str) -> Role | None:
        return self._store.get_role(role_id)

    def list(self) -> tuple[Role, ...]:
        return self._store.list_roles()

    def remove(self, role_id: str) -> bool:
        return self._store.delete_role(role_id)

    def update(self, role: Role) -> None:
        if self._store.get_role(role.id) is None:
            raise KeyError(role.id)

        self._store.save_role(role)


class SQLiteAssignmentStore:
    """Implementa el contrato de AssignmentStore con persistencia SQLite."""

    def __init__(self, store: SQLiteSecurityStore) -> None:
        self._store = store

    def add(self, assignment: ActorRoleAssignment) -> None:
        # Una asignación debe referenciar un rol persistido.
        # Si ya existe, conservamos su definición canónica.
        if self._store.get_role(assignment.role.id) is None:
            self._store.save_role(assignment.role)

        self._store.save_assignment(assignment)

    def list(self) -> tuple[ActorRoleAssignment, ...]:
        return self._store.list_assignments()

    def remove(self, assignment: ActorRoleAssignment) -> bool:
        return self._store.delete_assignment(assignment)
