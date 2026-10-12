from security.assignment_store import AssignmentStore
from security.assignments import ActorRoleAssignment
from security.authorization import AuthorizationService
from security.models import Actor
from security.permissions import Permission, PermissionAction
from security.roles import Role


def make_role(permission: Permission) -> Role:
    return Role(
        id="role-1",
        name="Rol de prueba",
        permissions=frozenset({permission}),
    )


def test_authorize_actor_with_assigned_permission() -> None:
    actor = Actor.user("user-1")
    permission = Permission("processes", PermissionAction.READ)
    store = AssignmentStore()
    store.add(ActorRoleAssignment(actor, make_role(permission)))

    service = AuthorizationService(store)

    assert service.is_allowed(actor, permission) is True


def test_deny_permission_not_granted() -> None:
    actor = Actor.user("user-1")
    read_permission = Permission("processes", PermissionAction.READ)
    execute_permission = Permission("processes", PermissionAction.EXECUTE)
    store = AssignmentStore()
    store.add(ActorRoleAssignment(actor, make_role(read_permission)))

    service = AuthorizationService(store)

    assert service.is_allowed(actor, execute_permission) is False


def test_deny_actor_without_assignment() -> None:
    actor = Actor.user("user-1")
    another_actor = Actor.user("user-2")
    permission = Permission("rules", PermissionAction.READ)
    store = AssignmentStore()
    store.add(
        ActorRoleAssignment(another_actor, make_role(permission))
    )

    service = AuthorizationService(store)

    assert service.is_allowed(actor, permission) is False


def test_authorization_is_independent_of_actor_display_name() -> None:
    assigned_actor = Actor.user("user-1", name="Nombre anterior")
    current_actor = Actor.user("user-1", name="Nombre actualizado")
    permission = Permission("processes", PermissionAction.READ)
    store = AssignmentStore()
    store.add(
        ActorRoleAssignment(assigned_actor, make_role(permission))
    )

    service = AuthorizationService(store)

    assert service.is_allowed(current_actor, permission) is True


def test_different_actor_types_do_not_share_permissions() -> None:
    assigned_actor = Actor.user("shared-id")
    service_actor = Actor.service("shared-id")
    permission = Permission("processes", PermissionAction.READ)
    store = AssignmentStore()
    store.add(
        ActorRoleAssignment(assigned_actor, make_role(permission))
    )

    service = AuthorizationService(store)

    assert service.is_allowed(service_actor, permission) is False


def test_revoked_assignment_denies_permission_immediately() -> None:
    actor = Actor.user("user-1")
    permission = Permission("processes", PermissionAction.READ)
    assignment = ActorRoleAssignment(actor, make_role(permission))
    store = AssignmentStore()
    store.add(assignment)
    service = AuthorizationService(store)

    assert service.is_allowed(actor, permission) is True

    store.remove(assignment)

    assert service.is_allowed(actor, permission) is False
