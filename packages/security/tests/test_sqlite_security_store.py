
from security.assignments import ActorRoleAssignment
from security.models import Actor
from security.permissions import Permission, PermissionAction
from security.roles import Role
from security.sqlite_security_store import SQLiteSecurityStore


def make_role() -> Role:
    return Role(
        id="operator",
        name="Operador local",
        permissions=frozenset(
            {
                Permission("system.open_app", PermissionAction.EXECUTE),
                Permission("processes", PermissionAction.READ),
            }
        ),
    )


def test_role_survives_reopening_database(tmp_path):
    database = tmp_path / "security.db"
    role = make_role()

    SQLiteSecurityStore(database).save_role(role)

    reopened = SQLiteSecurityStore(database)

    assert reopened.get_role(role.id) == role


def test_assignment_survives_reopening_database(tmp_path):
    database = tmp_path / "security.db"
    role = make_role()
    actor = Actor.user("user-123", name="Usuario de prueba")
    assignment = ActorRoleAssignment(actor=actor, role=role)

    store = SQLiteSecurityStore(database)
    store.save_role(role)
    store.save_assignment(assignment)

    reopened = SQLiteSecurityStore(database)

    assert reopened.list_assignments() == (assignment,)


def test_deleting_role_removes_its_assignments(tmp_path):
    store = SQLiteSecurityStore(tmp_path / "security.db")
    role = make_role()
    assignment = ActorRoleAssignment(
        actor=Actor.user("user-123"),
        role=role,
    )

    store.save_role(role)
    store.save_assignment(assignment)

    assert store.delete_role(role.id) is True
    assert store.list_assignments() == ()


def test_duplicate_assignment_is_ignored(tmp_path):
    store = SQLiteSecurityStore(tmp_path / "security.db")
    role = make_role()
    assignment = ActorRoleAssignment(
        actor=Actor.user("user-123"),
        role=role,
    )

    store.save_role(role)
    store.save_assignment(assignment)
    store.save_assignment(assignment)

    assert store.list_assignments() == (assignment,)


def test_delete_missing_assignment_returns_false(tmp_path):
    store = SQLiteSecurityStore(tmp_path / "security.db")
    role = make_role()
    assignment = ActorRoleAssignment(
        actor=Actor.user("user-123"),
        role=role,
    )

    store.save_role(role)

    assert store.delete_assignment(assignment) is False

def test_in_memory_database_supports_multiple_operations():
    store = SQLiteSecurityStore(":memory:")
    role = make_role()

    store.save_role(role)

    assert store.get_role(role.id) == role
