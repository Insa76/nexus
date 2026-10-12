from security.permissions import Permission, PermissionAction


def test_create_permission() -> None:
    permission = Permission(
        resource="processes",
        action=PermissionAction.READ,
    )

    assert permission.resource == "processes"
    assert permission.action == PermissionAction.READ
    assert permission.key == "processes:read"


def test_permission_key_is_stable() -> None:
    permission = Permission(
        resource="rules",
        action=PermissionAction.EXECUTE,
    )

    assert permission.key == "rules:execute"
