from documents import build_document_services
from documents.context_resolver import (
    DocumentContext,
    DocumentContextSelection,
    DocumentContextResolver,
)

from context.models import (
    AssistantContext,
    OrganizationProfile,
    ProjectContext,
    UserProfile,
)
from documents.context_relevance import (
    DocumentContextRelevance,
)


def test_document_context_is_empty_for_selection():
    selection = DocumentContextSelection(
        user_id="user-a",
    )

    context = DocumentContext.empty(
        selection,
    )

    assert context.selection == selection
    assert context.documents == ()


def test_document_context_resolver_returns_documents_for_context():
    services = build_document_services()

    document = services.access.create_document(
        name="Documento",
        mime_type="text/plain",
        source="document.txt",
        user_id="user-a",
        organization_id="organization-a",
        project_id="project-a",
    )

    resolver = DocumentContextResolver(
        services.access,
    )

    result = resolver.resolve(
        user_id="user-a",
        organization_id="organization-a",
        project_ids=("project-a",),
    )

    assert result.documents == (document,)
    assert result.selection == DocumentContextSelection(
        user_id="user-a",
        organization_id="organization-a",
        project_ids=("project-a",),
    )


def test_document_context_resolver_returns_empty_context_when_no_documents_match():
    services = build_document_services()

    services.access.create_document(
        name="Documento",
        mime_type="text/plain",
        source="document.txt",
        user_id="user-a",
    )

    resolver = DocumentContextResolver(
        services.access,
    )

    result = resolver.resolve(
        user_id="user-b",
    )

    assert result.documents == ()
    assert result.selection == DocumentContextSelection(
        user_id="user-b",
    )


def test_document_context_resolver_resolves_multiple_projects():
    services = build_document_services()

    project_a_document = services.access.create_document(
        name="Proyecto A",
        mime_type="text/plain",
        source="a.txt",
        user_id="user-a",
        organization_id="organization-a",
        project_id="project-a",
    )

    project_b_document = services.access.create_document(
        name="Proyecto B",
        mime_type="text/plain",
        source="b.txt",
        user_id="user-a",
        organization_id="organization-a",
        project_id="project-b",
    )

    other_user_document = services.access.create_document(
        name="Otro usuario",
        mime_type="text/plain",
        source="other.txt",
        user_id="user-b",
        organization_id="organization-a",
        project_id="project-a",
    )

    resolver = DocumentContextResolver(
        services.access,
    )

    result = resolver.resolve(
        user_id="user-a",
        organization_id="organization-a",
        project_ids=("project-a", "project-b"),
    )

    assert result.documents == (
        project_a_document,
        project_b_document,
    )

    assert other_user_document not in result.documents

    assert result.selection == DocumentContextSelection(
        user_id="user-a",
        organization_id="organization-a",
        project_ids=("project-a", "project-b"),
    )


def test_document_context_is_immutable():
    services = build_document_services()

    document = services.access.create_document(
        name="Documento",
        mime_type="text/plain",
        source="document.txt",
        user_id="user-a",
    )

    resolver = DocumentContextResolver(
        services.access,
    )

    result = resolver.resolve(
        user_id="user-a",
    )

    assert isinstance(result.documents, tuple)
    assert result.documents == (document,)
    assert isinstance(result.selection, DocumentContextSelection)

def test_document_context_resolver_resolves_from_assistant_context():
    services = build_document_services()

    user = UserProfile.create(
        name="Carlos",
        organization_id="organization-a",
    )

    organization = OrganizationProfile.create(
        name="Organization A",
    )

    project_a = ProjectContext.create(
        name="Project A",
        organization_id="organization-a",
    )

    project_b = ProjectContext.create(
        name="Project B",
        organization_id="organization-a",
    )

    document_a = services.access.create_document(
        name="Documento A",
        mime_type="text/plain",
        source="a.txt",
        user_id=user.id,
        organization_id=organization.id,
        project_id=project_a.id,
    )

    document_b = services.access.create_document(
        name="Documento B",
        mime_type="text/plain",
        source="b.txt",
        user_id=user.id,
        organization_id=organization.id,
        project_id=project_b.id,
    )

    context = AssistantContext(
        user=user,
        organization=organization,
        projects=(project_a, project_b),
    )

    resolver = DocumentContextResolver(
        services.access,
    )

    result = resolver.resolve_from_context(
        context,
    )

    assert result.documents == (
        document_a,
        document_b,
    )

    assert result.selection.user_id == user.id
    assert result.selection.organization_id == organization.id
    assert result.selection.project_ids == (
        project_a.id,
        project_b.id,
    )

def test_document_context_contains_relevance_matches():
    services = build_document_services()

    document = services.access.create_document(
        name="Documento",
        mime_type="text/plain",
        source="document.txt",
        user_id="user-a",
        organization_id="organization-a",
        project_id="project-a",
    )

    resolver = DocumentContextResolver(
        services.access,
    )

    result = resolver.resolve(
        user_id="user-a",
        organization_id="organization-a",
        project_ids=("project-a",),
    )

    assert result.documents == (document,)
    assert len(result.matches) == 1
    assert result.matches[0].document == document
    assert (
        result.matches[0].relevance
        == DocumentContextRelevance.PROJECT
    )


def test_empty_document_context_contains_no_matches():
    selection = DocumentContextSelection(
        user_id="user-a",
    )

    context = DocumentContext.empty(
        selection,
    )

    assert context.documents == ()
    assert context.matches == ()

def test_ordered_matches_returns_most_specific_context_first():
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

    resolver = DocumentContextResolver(
        services.access,
    )

    result = resolver.resolve(
        user_id="user-a",
        organization_id="organization-a",
        project_ids=("project-a",),
    )

    ordered = result.ordered_matches()

    assert [match.document for match in ordered] == [
        project_document,
        organization_document,
        user_document,
    ]


def test_ordered_matches_does_not_change_original_document_order():
    services = build_document_services()

    first = services.access.create_document(
        name="First",
        mime_type="text/plain",
        source="first.txt",
        user_id="user-a",
    )

    second = services.access.create_document(
        name="Second",
        mime_type="text/plain",
        source="second.txt",
        user_id="user-a",
        organization_id="organization-a",
    )

    resolver = DocumentContextResolver(
        services.access,
    )

    result = resolver.resolve(
        user_id="user-a",
        organization_id="organization-a",
    )

    assert result.documents == (
        first,
        second,
    )

    assert result.ordered_matches() == (
        result.matches[1],
        result.matches[0],
    )

    assert result.documents == (
        first,
        second,
    )

def test_ordered_documents_returns_documents_by_context_relevance():
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

    resolver = DocumentContextResolver(
        services.access,
    )

    result = resolver.resolve(
        user_id="user-a",
        organization_id="organization-a",
        project_ids=("project-a",),
    )

    assert result.ordered_documents() == (
        project_document,
        organization_document,
        user_document,
    )


def test_ordered_documents_does_not_change_documents():
    services = build_document_services()

    first = services.access.create_document(
        name="First",
        mime_type="text/plain",
        source="first.txt",
        user_id="user-a",
    )

    second = services.access.create_document(
        name="Second",
        mime_type="text/plain",
        source="second.txt",
        user_id="user-a",
        organization_id="organization-a",
    )

    resolver = DocumentContextResolver(
        services.access,
    )

    result = resolver.resolve(
        user_id="user-a",
        organization_id="organization-a",
    )

    assert result.documents == (
        first,
        second,
    )

    assert result.ordered_documents() == (
        second,
        first,
    )

def test_documents_by_mime_type_filters_resolved_documents():
    services = build_document_services()

    text_document = services.access.create_document(
        name="Texto",
        mime_type="text/plain",
        source="texto.txt",
        user_id="user-a",
    )

    json_document = services.access.create_document(
        name="Datos",
        mime_type="application/json",
        source="datos.json",
        user_id="user-a",
    )

    resolver = DocumentContextResolver(
        services.access,
    )

    result = resolver.resolve(
        user_id="user-a",
    )

    assert result.documents_by_mime_type(
        "text/plain",
    ) == (
        text_document,
    )

    assert result.documents_by_mime_type(
        "application/json",
    ) == (
        json_document,
    )


def test_documents_by_name_filters_case_insensitively():
    services = build_document_services()

    first = services.access.create_document(
        name="Manual de Operaciones",
        mime_type="text/plain",
        source="manual.txt",
        user_id="user-a",
    )

    services.access.create_document(
        name="Contrato Comercial",
        mime_type="text/plain",
        source="contrato.txt",
        user_id="user-a",
    )

    resolver = DocumentContextResolver(
        services.access,
    )

    result = resolver.resolve(
        user_id="user-a",
    )

    assert result.documents_by_name(
        "OPERACIONES",
    ) == (
        first,
    )

def test_empty_context_filters_return_empty_tuples():
    selection = DocumentContextSelection(
        user_id="user-a",
    )

    context = DocumentContext.empty(
        selection,
    )

    assert context.documents_by_mime_type(
        "text/plain",
    ) == ()

    assert context.documents_by_name(
        "contrato",
    ) == ()

    assert context.ordered_matches() == ()

    assert context.ordered_documents() == ()

def test_context_filter_applies_name_and_mime_type_filters():
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

    services.access.create_document(
        name="Informe Comercial",
        mime_type="application/pdf",
        source="informe.pdf",
        user_id="user-a",
    )

    resolver = DocumentContextResolver(
        services.access,
    )

    result = resolver.resolve(
        user_id="user-a",
    )

    assert result.filter(
        name="CONTRATO",
        mime_type="application/pdf",
    ) == (
        matching,
    )


def test_context_filter_without_filters_returns_original_documents():
    services = build_document_services()

    first = services.access.create_document(
        name="Primero",
        mime_type="text/plain",
        source="first.txt",
        user_id="user-a",
    )

    second = services.access.create_document(
        name="Segundo",
        mime_type="application/json",
        source="second.json",
        user_id="user-a",
    )

    resolver = DocumentContextResolver(
        services.access,
    )

    result = resolver.resolve(
        user_id="user-a",
    )

    assert result.filter() == (
        first,
        second,
    )


def test_context_filter_preserves_document_order():
    services = build_document_services()

    first = services.access.create_document(
        name="Contrato A",
        mime_type="application/pdf",
        source="a.pdf",
        user_id="user-a",
    )

    second = services.access.create_document(
        name="Contrato B",
        mime_type="application/pdf",
        source="b.pdf",
        user_id="user-a",
    )

    resolver = DocumentContextResolver(
        services.access,
    )

    result = resolver.resolve(
        user_id="user-a",
    )

    assert result.filter(
        name="contrato",
        mime_type="application/pdf",
    ) == (
        first,
        second,
    )

def test_context_query_returns_structured_result():
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

    resolver = DocumentContextResolver(
        services.access,
    )

    context = resolver.resolve(
        user_id="user-a",
    )

    result = context.query(
        name="contrato",
        mime_type="application/pdf",
    )

    assert result.documents == (
        matching,
    )

    assert result.total == 1

    assert result.query == {
        "name": "contrato",
        "mime_type": "application/pdf",
    }


def test_context_query_without_filters_returns_all_context_documents():
    services = build_document_services()

    first = services.access.create_document(
        name="Primero",
        mime_type="text/plain",
        source="first.txt",
        user_id="user-a",
    )

    second = services.access.create_document(
        name="Segundo",
        mime_type="application/pdf",
        source="second.pdf",
        user_id="user-a",
    )

    resolver = DocumentContextResolver(
        services.access,
    )

    context = resolver.resolve(
        user_id="user-a",
    )

    result = context.query()

    assert result.documents == (
        first,
        second,
    )

    assert result.total == 2

    assert result.query == {}

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

def test_context_query_preserves_relevance_matches():
    services = build_document_services()

    user_document = services.access.create_document(
        name="Contrato Usuario",
        mime_type="application/pdf",
        source="user.pdf",
        user_id="user-a",
    )

    project_document = services.access.create_document(
        name="Contrato Proyecto",
        mime_type="application/pdf",
        source="project.pdf",
        user_id="user-a",
        organization_id="organization-a",
        project_id="project-a",
    )

    resolver = DocumentContextResolver(
        services.access,
    )

    context = resolver.resolve(
        user_id="user-a",
        organization_id="organization-a",
        project_ids=("project-a",),
    )


    result = context.query(
        name="contrato",
        mime_type="application/pdf",
    )

    assert result.documents == (
        user_document,
        project_document,
    )

    assert result.ordered_documents() == (
        project_document,
        user_document,
    )

def test_context_query_supports_offset_and_limit():
    services = build_document_services()

    first = services.access.create_document(
        name="Documento Primero",
        mime_type="text/plain",
        source="first.txt",
        user_id="user-a",
    )

    second = services.access.create_document(
        name="Documento Segundo",
        mime_type="text/plain",
        source="second.txt",
        user_id="user-a",
    )

    third = services.access.create_document(
        name="Documento Tercero",
        mime_type="text/plain",
        source="third.txt",
        user_id="user-a",
    )

    resolver = DocumentContextResolver(
        services.access,
    )

    context = resolver.resolve(
        user_id="user-a",
    )

    result = context.query(
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


def test_context_query_pagination_preserves_relevance_matches():
    services = build_document_services()

    user_document = services.access.create_document(
        name="Contrato Usuario",
        mime_type="application/pdf",
        source="user.pdf",
        user_id="user-a",
    )

    project_document = services.access.create_document(
        name="Contrato Proyecto",
        mime_type="application/pdf",
        source="project.pdf",
        user_id="user-a",
        organization_id="organization-a",
        project_id="project-a",
    )

    resolver = DocumentContextResolver(
        services.access,
    )

    context = resolver.resolve(
        user_id="user-a",
        organization_id="organization-a",
        project_ids=("project-a",),
    )

    result = context.query(
        name="contrato",
        offset=1,
        limit=1,
    )

    assert result.documents == (
        project_document,
    )

    assert result.total == 2
    assert result.matches == (
        next(
            match
            for match in context.matches
            if match.document == project_document
        ),
    )
