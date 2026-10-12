from __future__ import annotations

from dataclasses import dataclass

from security.permissions import Permission


@dataclass(frozen=True, slots=True)
class Role:
    """
    Conjunto de permisos asignado a un actor.
    """

    id: str
    name: str
    permissions: frozenset[Permission]

    def has_permission(
        self,
        permission: Permission,
    ) -> bool:
        return permission in self.permissions
