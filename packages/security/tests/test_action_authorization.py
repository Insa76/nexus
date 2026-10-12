from security.action_authorization import ActionAuthorization
from security.action_policy import ActionPolicy
from security.action_policy_store import ActionPolicyStore
from security.assignment_capability import AssignmentCapability
from security.assignment_store import AssignmentStore
from security.assignments import ActorRoleAssignment
from security.authorization import AuthorizationService
from security.models import Actor
from security.permissions import Permission, PermissionAction
from security.roles import Role


def make_service() -> tuple[ActionAuthorization, Actor]:
    actor = Actor.user("user-1")
    permission = Permission("system", PermissionAction.EXECUTE)

    role = Role(
        id="role-1",
        name="Ejecutor del sistema",
        permissions=frozenset({permission}),
    )

    assignment_store = AssignmentStore()
    AssignmentCapability(assignment_store).assign(
        ActorRoleAssignment(actor=actor, role=role)
    )

    policy_store = ActionPolicyStore()
    policy_store.register(
        ActionPolicy(
            action_name="system.open_app",
            permission=permission,
        )
    )

    authorization = AuthorizationService(assignment_store)

    return ActionAuthorization(
        policy_store=policy_store,
        authorization=authorization,
    ), actor


def test_authorize_action_with_required_permission() -> None:
    service, actor = make_service()

    assert service.is_allowed(actor, "system.open_app") is True


def test_deny_action_without_policy() -> None:
    service, actor = make_service()

    assert service.is_allowed(actor, "system.close_app") is False


def test_deny_action_without_required_permission() -> None:
    service, _ = make_service()
    actor_without_role = Actor.user("user-2")

    assert service.is_allowed(
        actor_without_role,
        "system.open_app",
    ) is False
