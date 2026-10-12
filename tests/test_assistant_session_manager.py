from context import (
    AssistantContext,
    AssistantSessionManager,
    OrganizationProfile,
    UserProfile,
)


def test_start_creates_active_session() -> None:
    manager = AssistantSessionManager()
    context = AssistantContext()

    session = manager.start(context)

    assert session.context is context
    assert manager.get_active() is session


def test_start_replaces_previous_active_session() -> None:
    manager = AssistantSessionManager()

    first_context = AssistantContext()
    second_context = AssistantContext()

    first_session = manager.start(first_context)
    second_session = manager.start(second_context)

    assert first_session is not second_session
    assert manager.get_active() is second_session
    assert manager.get_active() is not first_session


def test_close_removes_active_session() -> None:
    manager = AssistantSessionManager()
    context = AssistantContext()

    session = manager.start(context)

    closed_session = manager.close()

    assert closed_session is session
    assert manager.get_active() is None


def test_close_without_active_session_is_safe() -> None:
    manager = AssistantSessionManager()

    assert manager.close() is None
    assert manager.get_active() is None


def test_session_keeps_user_and_organization_context() -> None:
    manager = AssistantSessionManager()

    organization = OrganizationProfile.create(
        "Organización Demo",
        industry="technology",
    )

    user = UserProfile.create(
        "Diego",
        role="Administrador",
        organization_id=organization.id,
    )

    context = AssistantContext(
        user=user,
        organization=organization,
    )

    session = manager.start(context)

    assert session.context.user is user
    assert session.context.organization is organization
