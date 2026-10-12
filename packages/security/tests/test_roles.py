from security.permissions import Permission, PermissionAction
from security.roles import Role


def test_role_contains_permission() -> None:
    permission = Permission(
        resource="processes",
        action=PermissionAction.READ,
    )

    role = Role(
        id="role-1",
        name="Procesos - lectura",
        permissions=frozenset({permission}),
    )

    assert role.has_permission(permission) is True


def test_role_rejects_missing_permission() -> None:
    read_permission = Permission(
        resource="processes",
        action=PermissionAction.READ,
    )

    execute_permission = Permission(
        resource="processes",
        action=PermissionAction.EXECUTE,
    )

    role = Role(
        id="role-1",
        name="Procesos - lectura",
        permissions=frozenset({read_permission}),
    )

    assert role.has_permission(execute_permission) is False
