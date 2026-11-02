
from bootstrap.bootstrap import build_engine
from context import (
    AssistantContext,
    AssistantSession,
    OrganizationProfile,
    UserProfile,
)


def test_bootstrap_can_inject_assistant_context() -> None:
    organization = OrganizationProfile.create(
        "Organización Demo",
        industry="technology",
    )

    user = UserProfile.create(
        "Diego",
        role="Administrador",
        organization_id=organization.id,
    )

    assistant_context = AssistantContext(
        user=user,
        organization=organization,
    )

    engine = build_engine(
        assistant_context=assistant_context,
    )

    assert engine._assistant_context is assistant_context
    assert (
        engine._context_builder._assistant_context
        is assistant_context
    )


def test_bootstrap_keeps_context_optional() -> None:
    engine = build_engine()

    assert isinstance(engine._assistant_context, AssistantContext)
    assert engine._assistant_context.user is None
    assert engine._assistant_context.organization is None
    assert (
        engine._context_builder._assistant_context
        is engine._assistant_context
    )


def test_bootstrap_can_inject_assistant_session() -> None:
    organization = OrganizationProfile.create(
        "Organización Demo",
        industry="technology",
    )

    user = UserProfile.create(
        "Diego",
        role="Administrador",
        organization_id=organization.id,
    )

    assistant_context = AssistantContext(
        user=user,
        organization=organization,
    )

    assistant_session = AssistantSession.create(
        assistant_context,
    )

    engine = build_engine(
        assistant_session=assistant_session,
    )

    assert engine._assistant_context is assistant_context
    assert (
        engine._context_builder._assistant_context
        is assistant_context
    )


def test_bootstrap_creates_session_from_context() -> None:
    organization = OrganizationProfile.create(
        "Organización Demo",
        industry="technology",
    )

    user = UserProfile.create(
        "Diego",
        role="Administrador",
        organization_id=organization.id,
    )

    assistant_context = AssistantContext(
        user=user,
        organization=organization,
    )

    assistant_session = AssistantSession.create(
        assistant_context,
    )

    engine = build_engine(
        assistant_session=assistant_session,
    )

    assert engine._assistant_context is assistant_context
    assert (
        engine._context_builder._assistant_context
        is assistant_context
    )
