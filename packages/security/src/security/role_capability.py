from __future__ import annotations

from dataclasses import dataclass

from security.role_store import RoleStore
from security.roles import Role


@dataclass(slots=True)
class RoleCapability:
    """Operaciones disponibles para gestionar roles de seguridad."""

    store: RoleStore

    def create(self, role: Role) -> Role:
        self.store.add(role)
        return role

    def get(self, role_id: str) -> Role | None:
        return self.store.get(role_id)

    def list(self) -> tuple[Role, ...]:
        return self.store.list()

    def update(self, role: Role) -> Role:
        self.store.update(role)
        return role

    def remove(self, role_id: str) -> bool:
        return self.store.remove(role_id)
