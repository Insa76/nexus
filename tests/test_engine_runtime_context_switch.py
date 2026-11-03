from bootstrap.bootstrap import build_engine
from context import AssistantContext, OrganizationProfile, UserProfile


def test_engine_can_switch_context_without_rebuilding():
    engine = build_engine()
    organization = OrganizationProfile.create("Organización activa")
    user = UserProfile.create(
        "Usuario activo",
        organization_id=organization.id,
    )
    context = AssistantContext(
        user=user,
        organization=organization,
    )

    engine.set_assistant_context(context)

    assert engine.assistant_context is context
    assert engine._context_builder._assistant_context is context

    cognitive_context = engine._context_builder.build(
        engine.memory,
        assistant_context=engine.assistant_context,
    )
    assert cognitive_context["assistant_context"]["user"]["name"] == "Usuario activo"
    assert (
        cognitive_context["assistant_context"]["organization"]["name"]
        == "Organización activa"
    )
