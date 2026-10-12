from context import (
    AssistantContext,
    ContextStore,
    OrganizationProfile,
    ProjectContext,
    UserProfile,
)

from memory import WorkingMemory

from planner.context_builder import ContextBuilder


def test_context_builder_includes_assistant_context():
    store = ContextStore()

    organization = OrganizationProfile.create(
        name="NEXUS Labs",
        industry="Software",
        description="Organización de desarrollo.",
        areas=["Technology", "Operations"],
        rules=["Security first"],
        priorities=["Reliability"],
    )

    user = UserProfile.create(
        name="Carlos",
        role="Founder",
        organization_id=organization.id,
        preferences={
            "language": "es",
        },
        responsibilities=[
            "Product",
            "Architecture",
        ],
        priorities=[
            "NEXUS",
        ],
    )

    project = ProjectContext.create(
        name="NEXUS",
        organization_id=organization.id,
        description="Cognitive runtime.",
        status="active",
        responsible_user_ids=[
            user.id,
        ],
    )

    store.add_organization(organization)
    store.add_user(user)
    store.add_project(project)

    assistant_context = store.build_context(
        user_id=user.id
    )

    memory = WorkingMemory()

    memory.add(
        "user_request",
        {
            "text": "Abrí Chrome",
        },
    )

    builder = ContextBuilder()

    context = builder.build(
        memory,
        assistant_context=assistant_context,
    )

    assert context["assistant_context"] is not None

    assert (
        context["assistant_context"]["user"]["name"]
        == "Carlos"
    )

    assert (
        context["assistant_context"]["organization"]["name"]
        == "NEXUS Labs"
    )

    assert (
        context["assistant_context"]["projects"][0]["name"]
        == "NEXUS"
    )


def test_context_builder_keeps_previous_behavior_without_assistant_context():
    memory = WorkingMemory()

    memory.add(
        "user_request",
        {
            "text": "Abrí Notepad",
        },
    )

    builder = ContextBuilder()

    context = builder.build(
        memory
    )

    assert context["assistant_context"] is None

    assert (
        context["last_request"]["text"]
        == "Abrí Notepad"
    )


def test_context_builder_can_keep_assistant_context_configured_in_constructor():
    organization = OrganizationProfile.create(
        name="NEXUS Labs",
        industry="Software",
    )

    user = UserProfile.create(
        name="Carlos",
        role="Founder",
        organization_id=organization.id,
    )

    project = ProjectContext.create(
        name="NEXUS",
        organization_id=organization.id,
    )

    assistant_context = AssistantContext(
        user=user,
        organization=organization,
        projects=[project],
    )

    builder = ContextBuilder(
        assistant_context=assistant_context
    )

    memory = WorkingMemory()

    context = builder.build(
        memory
    )

    assert (
        context["assistant_context"]["user"]["id"]
        == user.id
    )

    assert (
        context["assistant_context"]["organization"]["id"]
        == organization.id
    )

    assert (
        context["assistant_context"]["projects"][0]["id"]
        == project.id
    )
