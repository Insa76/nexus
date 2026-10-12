import pytest

from security.permissions import Permission, PermissionAction
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


def test_add_and_get_role() -> None:
    store = RoleStore()
    role = make_role()

    store.add(role)

    assert store.get(role.id) == role


def test_reject_duplicate_role_id() -> None:
    store = RoleStore()
    store.add(make_role())

    with pytest.raises(ValueError, match="Role already exists"):
        store.add(make_role())


def test_list_roles() -> None:
    store = RoleStore()
    first = make_role("role-1")
    second = make_role("role-2", "Administrador")

    store.add(first)
    store.add(second)

    assert store.list() == (first, second)


def test_update_existing_role() -> None:
    store = RoleStore()
    store.add(make_role())

    updated = make_role(name="Lector actualizado")
    store.update(updated)

    assert store.get("role-1") == updated


def test_update_missing_role_raises() -> None:
    store = RoleStore()

    with pytest.raises(KeyError, match="Role not found"):
        store.update(make_role())


def test_remove_role() -> None:
    store = RoleStore()
    store.add(make_role())

    assert store.remove("role-1") is True
    assert store.get("role-1") is None


def test_remove_missing_role() -> None:
    store = RoleStore()

    assert store.remove("inexistente") is False
