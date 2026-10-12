from context.models import (
    AssistantContext,
    OrganizationProfile,
    ProjectContext,
    UserProfile,
)

from documents import build_document_services
from documents.context_access import DocumentContextAccess
from documents.context_resolver import DocumentContextResolver


def build_context_access() -> DocumentContextAccess:
    services = build_document_services()

    resolver = DocumentContextResolver(
        services.access,
    )

    return DocumentContextAccess(
        resolver,
    )


def test_context_access_resolves_documents():
    services = build_document_services()

    document = services.access.create_document(
        name="Documento",
        mime_type="text/plain",
        source="document.txt",
        user_id="user-a",
    )

    access = DocumentContextAccess(
        DocumentContextResolver(
            services.access,
        )
    )

    result = access.resolve(
        user_id="user-a",
    )

    assert result.documents == (document,)


def test_context_access_resolves_from_assistant_context():
    services = build_document_services()

    user = UserProfile.create(
        name="Carlos",
    )

    project = ProjectContext.create(
        name="Proyecto A",
        organization_id="organization-a",
    )

    document = services.access.create_document(
        name="Documento",
        mime_type="text/plain",
        source="document.txt",
        user_id=user.id,
        project_id=project.id,
    )

    context = AssistantContext(
        user=user,
        projects=(project,),
    )

    access = DocumentContextAccess(
        DocumentContextResolver(
            services.access,
        )
    )

    result = access.resolve_from_context(
        context,
    )

    assert result.documents == (document,)


def test_context_access_preserves_context_selection():
    access = build_context_access()

    context = AssistantContext(
        user=UserProfile.create(
            name="Carlos",
        ),
        projects=(
            ProjectContext.create(
                name="Proyecto A",
                organization_id="organization-a",
            ),
        ),
    )

    result = access.resolve_from_context(
        context,
    )

    assert result.selection.user_id == context.user.id
    assert result.selection.project_ids == (
        context.projects[0].id,
    )

def test_context_access_resolves_ordered_matches():
    services = build_document_services()

    user_document = services.access.create_document(
        name="Usuario",
        mime_type="text/plain",
        source="user.txt",
        user_id="user-a",
    )

    organization_document = services.access.create_document(
        name="Organización",
        mime_type="text/plain",
        source="organization.txt",
        user_id="user-a",
        organization_id="organization-a",
    )

    project_document = services.access.create_document(
        name="Proyecto",
        mime_type="text/plain",
        source="project.txt",
        user_id="user-a",
        organization_id="organization-a",
        project_id="project-a",
    )

    ordered = services.context_access.resolve_ordered_matches(
        user_id="user-a",
        organization_id="organization-a",
        project_ids=("project-a",),
    )

    assert tuple(match.document for match in ordered) == (
        project_document,
        organization_document,
        user_document,
    )


def test_context_access_resolves_ordered_documents():
    services = build_document_services()

    user_document = services.access.create_document(
        name="Usuario",
        mime_type="text/plain",
        source="user.txt",
        user_id="user-a",
    )

    organization_document = services.access.create_document(
        name="Organización",
        mime_type="text/plain",
        source="organization.txt",
        user_id="user-a",
        organization_id="organization-a",
    )

    project_document = services.access.create_document(
        name="Proyecto",
        mime_type="text/plain",
        source="project.txt",
        user_id="user-a",
        organization_id="organization-a",
        project_id="project-a",
    )

    ordered = services.context_access.resolve_ordered_documents(
        user_id="user-a",
        organization_id="organization-a",
        project_ids=("project-a",),
    )

    assert ordered == (
        project_document,
        organization_document,
        user_document,
    )

def test_context_access_resolves_ordered_matches_from_assistant_context():
    services = build_document_services()

    user = UserProfile.create(
        name="Carlos",
        organization_id="organization-a",
    )

    organization = OrganizationProfile.create(
        name="Organization A",
    )

    project = ProjectContext.create(
        name="Project A",
        organization_id="organization-a",
    )

    user_document = services.access.create_document(
        name="Usuario",
        mime_type="text/plain",
        source="user.txt",
        user_id=user.id,
    )

    organization_document = services.access.create_document(
        name="Organización",
        mime_type="text/plain",
        source="organization.txt",
        user_id=user.id,
        organization_id=organization.id,
    )

    project_document = services.access.create_document(
        name="Proyecto",
        mime_type="text/plain",
        source="project.txt",
        user_id=user.id,
        organization_id=organization.id,
        project_id=project.id,
    )

    context = AssistantContext(
        user=user,
        organization=organization,
        projects=(project,),
    )

    ordered = services.context_access.resolve_ordered_matches_from_context(
        context,
    )

    assert tuple(match.document for match in ordered) == (
        project_document,
        organization_document,
        user_document,
    )


def test_context_access_resolves_ordered_documents_from_assistant_context():
    services = build_document_services()

    user = UserProfile.create(
        name="Carlos",
        organization_id="organization-a",
    )

    organization = OrganizationProfile.create(
        name="Organization A",
    )

    project = ProjectContext.create(
        name="Project A",
        organization_id="organization-a",
    )

    user_document = services.access.create_document(
        name="Usuario",
        mime_type="text/plain",
        source="user.txt",
        user_id=user.id,
    )

    organization_document = services.access.create_document(
        name="Organización",
        mime_type="text/plain",
        source="organization.txt",
        user_id=user.id,
        organization_id=organization.id,
    )

    project_document = services.access.create_document(
        name="Proyecto",
        mime_type="text/plain",
        source="project.txt",
        user_id=user.id,
        organization_id=organization.id,
        project_id=project.id,
    )

    context = AssistantContext(
        user=user,
        organization=organization,
        projects=(project,),
    )

    ordered = services.context_access.resolve_ordered_documents_from_context(
        context,
    )

    assert ordered == (
        project_document,
        organization_document,
        user_document,
    )

def test_context_access_query_returns_structured_document_result():
    services = build_document_services()

    matching = services.access.create_document(
        name="Contrato Comercial",
        mime_type="application/pdf",
        source="contrato.pdf",
        user_id="user-a",
    )

    services.access.create_document(
        name="Contrato Comercial",
        mime_type="text/plain",
        source="contrato.txt",
        user_id="user-a",
    )

    result = services.context_access.query(
        user_id="user-a",
        name="contrato",
        mime_type="application/pdf",
    )

    assert result.documents == (
        matching,
    )

    assert result.total == 1
    assert result.has_results is True
    assert result.query == {
        "name": "contrato",
        "mime_type": "application/pdf",
    }


def test_context_access_query_from_assistant_context():
    services = build_document_services()

    user = UserProfile.create(
        name="Carlos",
        organization_id="organization-a",
    )

    organization = OrganizationProfile.create(
        name="Organization A",
    )

    document = services.access.create_document(
        name="Contrato Comercial",
        mime_type="application/pdf",
        source="contrato.pdf",
        user_id=user.id,
        organization_id=organization.id,
    )

    context = AssistantContext(
        user=user,
        organization=organization,
    )

    result = services.context_access.query_from_context(
        context,
        name="contrato",
        mime_type="application/pdf",
    )

    assert result.documents == (
        document,
    )

    assert result.total == 1
    assert result.has_results is True

def test_context_access_query_supports_pagination():
    services = build_document_services()

    first = services.access.create_document(
        name="Primero",
        mime_type="text/plain",
        source="first.txt",
        user_id="user-a",
    )

    second = services.access.create_document(
        name="Segundo",
        mime_type="text/plain",
        source="second.txt",
        user_id="user-a",
    )

    third = services.access.create_document(
        name="Tercero",
        mime_type="text/plain",
        source="third.txt",
        user_id="user-a",
    )

    result = services.context_access.query(
        user_id="user-a",
        offset=1,
        limit=1,
    )

    assert result.documents == (
        second,
    )

    assert result.total == 3
    assert result.offset == 1
    assert result.limit == 1
    assert result.has_more is True


def test_context_access_query_from_context_supports_pagination():
    services = build_document_services()

    user = UserProfile.create(
        name="Carlos",
        organization_id="organization-a",
    )

    first = services.access.create_document(
        name="Primero",
        mime_type="text/plain",
        source="first.txt",
        user_id=user.id,
    )

    second = services.access.create_document(
        name="Segundo",
        mime_type="text/plain",
        source="second.txt",
        user_id=user.id,
    )

    context = AssistantContext(
        user=user,
    )

    result = services.context_access.query_from_context(
        context,
        offset=1,
        limit=1,
    )

    assert result.documents == (
        second,
    )

    assert result.total == 2
    assert result.offset == 1
    assert result.limit == 1
