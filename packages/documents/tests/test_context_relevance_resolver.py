from documents.context_relevance import (
    DocumentContextMatch,
    DocumentContextRelevance,
)
from documents.context_relevance_resolver import (
    DocumentContextRelevanceResolver,
)
from documents.context_resolver import DocumentContextSelection
from documents.models import Document


def test_project_document_has_project_relevance():
    document = Document.create(
        name="Documento",
        mime_type="text/plain",
        source="document.txt",
        user_id="user-a",
        organization_id="organization-a",
        project_id="project-a",
    )

    selection = DocumentContextSelection(
        user_id="user-a",
        organization_id="organization-a",
        project_ids=("project-a",),
    )

    result = DocumentContextRelevanceResolver().resolve(
        document=document,
        selection=selection,
    )

    assert result == DocumentContextMatch(
        document=document,
        relevance=DocumentContextRelevance.PROJECT,
    )


def test_organization_document_has_organization_relevance():
    document = Document.create(
        name="Documento",
        mime_type="text/plain",
        source="document.txt",
        user_id="user-a",
        organization_id="organization-a",
    )

    selection = DocumentContextSelection(
        user_id="user-a",
        organization_id="organization-a",
    )

    result = DocumentContextRelevanceResolver().resolve(
        document=document,
        selection=selection,
    )

    assert result == DocumentContextMatch(
        document=document,
        relevance=DocumentContextRelevance.ORGANIZATION,
    )


def test_user_document_has_user_relevance():
    document = Document.create(
        name="Documento",
        mime_type="text/plain",
        source="document.txt",
        user_id="user-a",
    )

    selection = DocumentContextSelection(
        user_id="user-a",
    )

    result = DocumentContextRelevanceResolver().resolve(
        document=document,
        selection=selection,
    )

    assert result == DocumentContextMatch(
        document=document,
        relevance=DocumentContextRelevance.USER,
    )


def test_document_without_context_match_returns_none():
    document = Document.create(
        name="Documento",
        mime_type="text/plain",
        source="document.txt",
        user_id="user-a",
    )

    selection = DocumentContextSelection(
        user_id="user-b",
    )

    result = DocumentContextRelevanceResolver().resolve(
        document=document,
        selection=selection,
    )

    assert result is None


def test_project_relevance_takes_precedence_over_organization_and_user():
    document = Document.create(
        name="Documento",
        mime_type="text/plain",
        source="document.txt",
        user_id="user-a",
        organization_id="organization-a",
        project_id="project-a",
    )

    selection = DocumentContextSelection(
        user_id="user-a",
        organization_id="organization-a",
        project_ids=("project-a",),
    )

    result = DocumentContextRelevanceResolver().resolve(
        document=document,
        selection=selection,
    )

    assert result is not None
    assert result.relevance == DocumentContextRelevance.PROJECT
