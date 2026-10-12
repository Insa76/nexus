from bootstrap.bootstrap import build_engine
from context import AssistantContext
from security import Actor


class User:
    def __init__(self, user_id: str) -> None:
        self.id = user_id


def get_action_authorization(engine):
    manager = engine._runtime.action_manager
    return manager._action_authorization


def test_local_console_has_explicit_permissions():
    engine = build_engine()

    authorization = get_action_authorization(engine)

    local_actor = Actor.system("local-console")

    assert authorization is not None
    assert authorization.is_allowed(
        local_actor,
        "system.open_app",
    )


def test_identified_user_does_not_inherit_local_permissions():
    context = AssistantContext(
        user=User("user-1"),
        organization=None,
        projects=[],
    )

    engine = build_engine(
        assistant_context=context,
    )

    authorization = get_action_authorization(engine)

    user_actor = Actor.user("user-1")

    assert authorization is not None
    assert not authorization.is_allowed(
        user_actor,
        "system.open_app",
    )


def test_unassigned_user_is_denied_for_other_actions():
    context = AssistantContext(
        user=User("user-2"),
        organization=None,
        projects=[],
    )

    engine = build_engine(
        assistant_context=context,
    )

    authorization = get_action_authorization(engine)

    assert authorization is not None
    assert not authorization.is_allowed(
        Actor.user("user-2"),
        "system.set_volume",
    )
