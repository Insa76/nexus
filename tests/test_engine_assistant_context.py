from context import (
    AssistantContext,
    OrganizationProfile,
    ProjectContext,
    UserProfile,
)

from memory import WorkingMemory

from planner.context_builder import ContextBuilder


def test_engine_context_builder_receives_assistant_context():
    organization = OrganizationProfile.create(
        name="NEXUS Labs",
        industry="Software",
        description="Organización de desarrollo.",
        areas=["Technology"],
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

    assistant_context = AssistantContext(
        user=user,
        organization=organization,
        projects=[project],
    )

    builder = ContextBuilder(
        assistant_context=assistant_context
    )

    memory = WorkingMemory()

    memory.add(
        "user_request",
        {
            "text": "Abrí Chrome",
        },
    )

    context = builder.build(
        memory,
        semantic_query="Abrí Chrome",
    )

    assistant = context["assistant_context"]

    assert assistant is not None

    assert assistant["user"]["id"] == user.id
    assert assistant["user"]["name"] == "Carlos"

    assert (
        assistant["organization"]["id"]
        == organization.id
    )

    assert (
        assistant["organization"]["name"]
        == "NEXUS Labs"
    )

    assert (
        assistant["projects"][0]["id"]
        == project.id
    )

    assert (
        assistant["projects"][0]["name"]
        == "NEXUS"
    )
