from __future__ import annotations

from dataclasses import dataclass, field

from security.roles import Role


@dataclass(slots=True)
class RoleStore:
    """Almacena roles de seguridad en memoria, identificados por ID."""

    _roles: dict[str, Role] = field(
        default_factory=dict,
        init=False,
        repr=False,
    )

    def add(self, role: Role) -> None:
        if role.id in self._roles:
            raise ValueError(f"Role already exists: {role.id}")

        self._roles[role.id] = role

    def get(self, role_id: str) -> Role | None:
        return self._roles.get(role_id)

    def list(self) -> tuple[Role, ...]:
        return tuple(self._roles.values())

    def remove(self, role_id: str) -> bool:
        return self._roles.pop(role_id, None) is not None

    def update(self, role: Role) -> None:
        if role.id not in self._roles:
            raise KeyError(f"Role not found: {role.id}")

        self._roles[role.id] = role
