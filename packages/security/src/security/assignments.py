from __future__ import annotations

from dataclasses import dataclass

from security.models import Actor
from security.roles import Role


@dataclass(frozen=True, slots=True)
class ActorRoleAssignment:
    """
    Asociación entre un actor y un rol de seguridad.
    """

    actor: Actor
    role: Role
