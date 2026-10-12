from security.assignment_capability import AssignmentCapability
from security.assignment_store import AssignmentStore
from security.assignments import ActorRoleAssignment
from security.models import Actor
from security.permissions import Permission, PermissionAction
from security.roles import Role


def make_assignment() -> ActorRoleAssignment:
    actor = Actor.user("user-1")
    permission = Permission("processes", PermissionAction.READ)
    role = Role(
        id="role-1",
        name="Lector de procesos",
        permissions=frozenset({permission}),
    )
    return ActorRoleAssignment(actor=actor, role=role)


def test_assign_and_list_roles() -> None:
    capability = AssignmentCapability(AssignmentStore())
    assignment = make_assignment()

    capability.assign(assignment)

    assert capability.list() == (assignment,)


def test_assign_duplicate_is_idempotent() -> None:
    capability = AssignmentCapability(AssignmentStore())
    assignment = make_assignment()

    capability.assign(assignment)
    capability.assign(assignment)

    assert capability.list() == (assignment,)


def test_revoke_assignment() -> None:
    capability = AssignmentCapability(AssignmentStore())
    assignment = make_assignment()
    capability.assign(assignment)

    assert capability.revoke(assignment) is True
    assert capability.list() == ()


def test_revoke_missing_assignment() -> None:
    capability = AssignmentCapability(AssignmentStore())

    assert capability.revoke(make_assignment()) is False
