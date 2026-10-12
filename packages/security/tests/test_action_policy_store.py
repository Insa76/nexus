import pytest

from security.action_policy import ActionPolicy
from security.action_policy_store import ActionPolicyStore
from security.permissions import Permission, PermissionAction


def make_policy(
    action_name: str = "system.open_app",
) -> ActionPolicy:
    return ActionPolicy(
        action_name=action_name,
        permission=Permission(
            resource="system",
            action=PermissionAction.EXECUTE,
        ),
    )


def test_register_and_get_policy() -> None:
    store = ActionPolicyStore()
    policy = make_policy()

    store.register(policy)

    assert store.get(policy.action_name) == policy


def test_reject_duplicate_policy() -> None:
    store = ActionPolicyStore()
    store.register(make_policy())

    with pytest.raises(ValueError, match="already registered"):
        store.register(make_policy())


def test_list_policies() -> None:
    store = ActionPolicyStore()
    first = make_policy()
    second = make_policy("system.close_app")

    store.register(first)
    store.register(second)

    assert store.list() == (first, second)


def test_remove_policy() -> None:
    store = ActionPolicyStore()
    store.register(make_policy())

    assert store.remove("system.open_app") is True
    assert store.get("system.open_app") is None


def test_remove_missing_policy() -> None:
    store = ActionPolicyStore()

    assert store.remove("inexistente") is False
