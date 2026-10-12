from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class PermissionAction(StrEnum):
    READ = "read"
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"
    EXECUTE = "execute"


@dataclass(frozen=True, slots=True)
class Permission:
    """
    Permiso elemental sobre un recurso de NEXUS.
    """

    resource: str
    action: PermissionAction

    @property
    def key(self) -> str:
        return f"{self.resource}:{self.action.value}"
