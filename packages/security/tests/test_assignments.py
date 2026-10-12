from security.models import Actor
from security.permissions import Permission, PermissionAction
from security.assignments import ActorRoleAssignment
from security.roles import Role


def test_assign_role_to_actor() -> None:
    actor = Actor.user("user-1")

    permission = Permission(
        resource="processes",
        action=PermissionAction.READ,
    )

    role = Role(
        id="role-1",
        name="Procesos - lectura",
        permissions=frozenset({permission}),
    )

    assignment = ActorRoleAssignment(
        actor=actor,
        role=role,
    )

    assert assignment.actor == actor
    assert assignment.role == role
