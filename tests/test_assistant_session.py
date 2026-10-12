from context import (
    AssistantContext,
    AssistantSession,
    OrganizationProfile,
    UserProfile,
)


def test_assistant_session_contains_active_context() -> None:
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

    session = AssistantSession.create(context)

    assert session.context is context
    assert session.session_id
    assert session.created_at.tzinfo is not None


def test_assistant_sessions_have_unique_ids() -> None:
    context = AssistantContext()

    session_a = AssistantSession.create(context)
    session_b = AssistantSession.create(context)

    assert session_a.session_id != session_b.session_id


def test_assistant_session_is_immutable() -> None:
    context = AssistantContext()
    session = AssistantSession.create(context)

    try:
        session.session_id = "changed"
    except AttributeError:
        pass
    else:
        raise AssertionError("AssistantSession should be immutable")
