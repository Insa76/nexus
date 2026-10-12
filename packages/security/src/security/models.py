from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class ActorType(StrEnum):
    USER = "user"
    SYSTEM = "system"
    SERVICE = "service"


@dataclass(frozen=True, slots=True)
class Actor:
    """
    Identidad que realiza una operación dentro de NEXUS.

    Security no decide permisos aquí.
    Este modelo solamente representa quién ejecuta la acción.
    """

    id: str
    actor_type: ActorType
    name: str | None = None

    @classmethod
    def user(
        cls,
        actor_id: str,
        *,
        name: str | None = None,
    ) -> Actor:
        return cls(
            id=actor_id,
            actor_type=ActorType.USER,
            name=name,
        )

    @classmethod
    def system(
        cls,
        actor_id: str = "system",
        *,
        name: str | None = None,
    ) -> Actor:
        return cls(
            id=actor_id,
            actor_type=ActorType.SYSTEM,
            name=name,
        )

    @classmethod
    def service(
        cls,
        actor_id: str,
        *,
        name: str | None = None,
    ) -> Actor:
        return cls(
            id=actor_id,
            actor_type=ActorType.SERVICE,
            name=name,
        )
