from security.action_policy import ActionPolicy
from security.permissions import Permission, PermissionAction


def test_action_policy_declares_required_permission() -> None:
    policy = ActionPolicy(
        action_name="system.open_app",
        permission=Permission(
            resource="system",
            action=PermissionAction.EXECUTE,
        ),
    )

    assert policy.action_name == "system.open_app"
    assert policy.permission.key == "system:execute"
