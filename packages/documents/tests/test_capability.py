from context import AssistantContext, OrganizationProfile, UserProfile

from documents import (
    DocumentCapability,
    build_document_services,
)
from unittest.mock import MagicMock

from documents.context_access import DocumentContextAccess

def test_document_capability_is_public():
    assert DocumentCapability is not None


def test_document_capability_queries_using_assistant_context():
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

    capability = DocumentCapability(
        context_access=services.context_access,
    )

    result = capability.query(
        context=context,
        name="contrato",
        mime_type="application/pdf",
    )

    assert result.documents == (document,)
    assert result.total == 1
    assert result.has_results


def test_document_capability_preserves_pagination():
    services = build_document_services()

    user = UserProfile.create(
        name="Carlos",
        organization_id="organization-a",
    )

    organization = OrganizationProfile.create(
        name="Organization A",
    )

    first = services.access.create_document(
        name="Contrato 1",
        mime_type="application/pdf",
        source="contrato-1.pdf",
        user_id=user.id,
        organization_id=organization.id,
    )

    second = services.access.create_document(
        name="Contrato 2",
        mime_type="application/pdf",
        source="contrato-2.pdf",
        user_id=user.id,
        organization_id=organization.id,
    )

    context = AssistantContext(
        user=user,
        organization=organization,
    )

    capability = DocumentCapability(
        context_access=services.context_access,
    )

    result = capability.query(
        context=context,
        name="contrato",
        offset=1,
        limit=1,
    )

    assert result.documents == (second,)
    assert result.total == 2
    assert result.offset == 1
    assert result.limit == 1
    assert result.has_more is False

def test_document_capability_returns_relevant_matches():
    context = MagicMock()
    context_access = MagicMock(spec=DocumentContextAccess)

    expected_matches = ("match-1", "match-2")
    context_access.resolve_ordered_matches_from_context.return_value = (
        expected_matches
    )

    capability = DocumentCapability(
        context_access=context_access,
    )

    result = capability.relevant(
        context=context,
    )

    assert result == expected_matches

    context_access.resolve_ordered_matches_from_context.assert_called_once_with(
        context,
    )


def test_document_capability_returns_relevant_documents():
    context = MagicMock()
    context_access = MagicMock(spec=DocumentContextAccess)

    expected_documents = ("document-1", "document-2")
    context_access.resolve_ordered_documents_from_context.return_value = (
        expected_documents
    )

    capability = DocumentCapability(
        context_access=context_access,
    )

    result = capability.relevant_documents(
        context=context,
    )

    assert result == expected_documents

    context_access.resolve_ordered_documents_from_context.assert_called_once_with(
        context,
    )
