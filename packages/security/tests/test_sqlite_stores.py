
import pytest

from security.assignment_store import AssignmentStore
from security.assignments import ActorRoleAssignment
from security.models import Actor
from security.permissions import Permission, PermissionAction
from security.role_store import RoleStore
from security.roles import Role
from security.sqlite_security_store import SQLiteSecurityStore
from security.sqlite_stores import (
    SQLiteAssignmentStore,
    SQLiteRoleStore,
)
from security.authorization import AuthorizationService


def make_role(
    role_id: str = "operator",
    name: str = "Operador",
) -> Role:
    return Role(
        id=role_id,
        name=name,
        permissions=frozenset(
            {
                Permission("processes", PermissionAction.READ),
            }
        ),
    )


def test_sqlite_role_store_preserves_role_store_contract(tmp_path):
    database = SQLiteSecurityStore(tmp_path / "security.db")
    roles = SQLiteRoleStore(database)
    role = make_role()

    roles.add(role)

    assert roles.get(role.id) == role
    assert roles.list() == (role,)
    assert roles.remove(role.id) is True
    assert roles.get(role.id) is None
    assert roles.remove(role.id) is False


def test_sqlite_role_store_rejects_duplicate_roles(tmp_path):
    roles = SQLiteRoleStore(
        SQLiteSecurityStore(tmp_path / "security.db")
    )
    role = make_role()
    roles.add(role)

    with pytest.raises(ValueError):
        roles.add(role)


def test_sqlite_role_store_update_requires_existing_role(tmp_path):
    roles = SQLiteRoleStore(
        SQLiteSecurityStore(tmp_path / "security.db")
    )

    with pytest.raises(KeyError):
        roles.update(make_role())


def test_sqlite_role_store_persists_updates(tmp_path):
    database_path = tmp_path / "security.db"
    roles = SQLiteRoleStore(SQLiteSecurityStore(database_path))
    original = make_role()
    updated = Role(
        id=original.id,
        name="Operador actualizado",
        permissions=frozenset(
            {
                Permission("processes", PermissionAction.READ),
                Permission("system", PermissionAction.EXECUTE),
            }
        ),
    )

    roles.add(original)
    roles.update(updated)

    reopened_roles = SQLiteRoleStore(
        SQLiteSecurityStore(database_path)
    )
    assert reopened_roles.get(updated.id) == updated


def test_sqlite_assignment_store_persists_assignments(tmp_path):
    database_path = tmp_path / "security.db"
    database = SQLiteSecurityStore(database_path)
    roles = SQLiteRoleStore(database)
    assignments = SQLiteAssignmentStore(database)

    role = make_role()
    assignment = ActorRoleAssignment(
        actor=Actor.user("user-123", name="Usuario de prueba"),
        role=role,
    )
    roles.add(role)
    assignments.add(assignment)

    reopened_database = SQLiteSecurityStore(database_path)
    reopened_assignments = SQLiteAssignmentStore(reopened_database)

    assert reopened_assignments.list() == (assignment,)


def test_sqlite_assignment_store_add_is_idempotent(tmp_path):
    database = SQLiteSecurityStore(tmp_path / "security.db")
    assignments = SQLiteAssignmentStore(database)
    assignment = ActorRoleAssignment(
        actor=Actor.user("user-123"),
        role=make_role(),
    )

    assignments.add(assignment)
    assignments.add(assignment)

    assert assignments.list() == (assignment,)


def test_sqlite_assignment_store_removes_assignment(tmp_path):
    database = SQLiteSecurityStore(tmp_path / "security.db")
    assignments = SQLiteAssignmentStore(database)
    assignment = ActorRoleAssignment(
        actor=Actor.user("user-123"),
        role=make_role(),
    )

    assignments.add(assignment)

    assert assignments.remove(assignment) is True
    assert assignments.list() == ()
    assert assignments.remove(assignment) is False


def test_existing_memory_stores_remain_available():
    assert RoleStore is not SQLiteRoleStore
    assert AssignmentStore is not SQLiteAssignmentStore


def test_authorization_allows_persisted_permission_after_reopening_database(
    tmp_path,
):
    database_path = tmp_path / "security.db"
    actor = Actor.user("user-123")
    role = make_role()
    assignment = ActorRoleAssignment(actor=actor, role=role)

    initial_database = SQLiteSecurityStore(database_path)
    SQLiteAssignmentStore(initial_database).add(assignment)

    reopened_database = SQLiteSecurityStore(database_path)
    authorization = AuthorizationService(
        SQLiteAssignmentStore(reopened_database)
    )

    assert authorization.is_allowed(
        actor,
        Permission("processes", PermissionAction.READ),
    ) is True


def test_authorization_denies_actor_without_persisted_assignment(
    tmp_path,
):
    database_path = tmp_path / "security.db"
    assigned_actor = Actor.user("user-123")
    other_actor = Actor.user("user-456")
    role = make_role()

    database = SQLiteSecurityStore(database_path)
    SQLiteAssignmentStore(database).add(
        ActorRoleAssignment(actor=assigned_actor, role=role)
    )

    reopened_database = SQLiteSecurityStore(database_path)
    authorization = AuthorizationService(
        SQLiteAssignmentStore(reopened_database)
    )

    assert authorization.is_allowed(
        other_actor,
        Permission("processes", PermissionAction.READ),
    ) is False


def test_authorization_denies_permission_not_granted_by_persisted_role(
    tmp_path,
):
    database_path = tmp_path / "security.db"
    actor = Actor.user("user-123")
    role = make_role()

    database = SQLiteSecurityStore(database_path)
    SQLiteAssignmentStore(database).add(
        ActorRoleAssignment(actor=actor, role=role)
    )

    reopened_database = SQLiteSecurityStore(database_path)
    authorization = AuthorizationService(
        SQLiteAssignmentStore(reopened_database)
    )

    assert authorization.is_allowed(
        actor,
        Permission("system.shutdown", PermissionAction.EXECUTE),
    ) is False
