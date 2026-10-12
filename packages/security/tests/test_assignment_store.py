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


def test_add_and_list_assignment() -> None:
    store = AssignmentStore()
    assignment = make_assignment()

    store.add(assignment)

    assert store.list() == (assignment,)


def test_duplicate_assignment_is_not_added() -> None:
    store = AssignmentStore()
    assignment = make_assignment()

    store.add(assignment)
    store.add(assignment)

    assert store.list() == (assignment,)


def test_remove_existing_assignment() -> None:
    store = AssignmentStore()
    assignment = make_assignment()
    store.add(assignment)

    assert store.remove(assignment) is True
    assert store.list() == ()


def test_remove_missing_assignment() -> None:
    store = AssignmentStore()

    assert store.remove(make_assignment()) is False
