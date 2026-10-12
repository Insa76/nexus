from __future__ import annotations

from dataclasses import dataclass

from security.permissions import Permission


@dataclass(frozen=True, slots=True)
class ActionPolicy:
    """Declara el permiso requerido para ejecutar una acción."""

    action_name: str
    permission: Permission
