import pytest

from security.permissions import Permission, PermissionAction
from security.role_capability import RoleCapability
from security.role_store import RoleStore
from security.roles import Role


def make_role(
    role_id: str = "role-1",
    name: str = "Lector de procesos",
) -> Role:
    permission = Permission("processes", PermissionAction.READ)
    return Role(
        id=role_id,
        name=name,
        permissions=frozenset({permission}),
    )


def test_create_and_get_role() -> None:
    capability = RoleCapability(RoleStore())
    role = make_role()

    assert capability.create(role) == role
    assert capability.get(role.id) == role


def test_list_roles() -> None:
    capability = RoleCapability(RoleStore())
    first = make_role()
    second = make_role("role-2", "Administrador")

    capability.create(first)
    capability.create(second)

    assert capability.list() == (first, second)


def test_update_role() -> None:
    capability = RoleCapability(RoleStore())
    capability.create(make_role())

    updated = make_role(name="Lector actualizado")

    assert capability.update(updated) == updated
    assert capability.get("role-1") == updated


def test_update_missing_role_raises() -> None:
    capability = RoleCapability(RoleStore())

    with pytest.raises(KeyError, match="Role not found"):
        capability.update(make_role())


def test_remove_role() -> None:
    capability = RoleCapability(RoleStore())
    capability.create(make_role())

    assert capability.remove("role-1") is True
    assert capability.get("role-1") is None
