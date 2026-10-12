from documents.models import Document
from documents.query import DocumentQueryResult


def test_document_query_result_stores_documents_and_total():
    first = Document.create(
        name="Primero",
        mime_type="text/plain",
        source="first.txt",
    )

    second = Document.create(
        name="Segundo",
        mime_type="application/pdf",
        source="second.pdf",
    )

    result = DocumentQueryResult(
        documents=(first, second),
        total=2,
    )

    assert result.documents == (
        first,
        second,
    )

    assert result.total == 2


def test_document_query_result_from_documents_calculates_total():
    document = Document.create(
        name="Documento",
        mime_type="text/plain",
        source="document.txt",
    )

    result = DocumentQueryResult.from_documents(
        (document,),
    )

    assert result.documents == (
        document,
    )

    assert result.total == 1


def test_document_query_result_preserves_query_metadata():
    document = Document.create(
        name="Contrato",
        mime_type="application/pdf",
        source="contrato.pdf",
    )

    result = DocumentQueryResult.from_documents(
        (document,),
        query={
            "name": "contrato",
            "mime_type": "application/pdf",
        },
    )

    assert result.query == {
        "name": "contrato",
        "mime_type": "application/pdf",
    }


def test_document_query_result_is_immutable():
    result = DocumentQueryResult(
        documents=(),
        total=0,
    )

    try:
        result.total = 1
    except AttributeError:
        pass
    else:
        raise AssertionError(
            "DocumentQueryResult should be immutable"
        )

def test_document_query_result_reports_empty_state():
    result = DocumentQueryResult(
        documents=(),
        total=0,
    )

    assert result.is_empty is True
    assert result.has_results is False


def test_document_query_result_reports_results_state():
    document = Document.create(
        name="Documento",
        mime_type="text/plain",
        source="document.txt",
    )

    result = DocumentQueryResult.from_documents(
        (document,),
    )

    assert result.is_empty is False
    assert result.has_results is True

def test_document_query_result_ordered_documents_uses_relevance():
    from documents.context_relevance import (
        DocumentContextMatch,
        DocumentContextRelevance,
    )

    user_document = Document.create(
        name="Usuario",
        mime_type="text/plain",
        source="user.txt",
    )

    project_document = Document.create(
        name="Proyecto",
        mime_type="text/plain",
        source="project.txt",
    )

    result = DocumentQueryResult.from_documents(
        (
            user_document,
            project_document,
        ),
        matches=(
            DocumentContextMatch(
                document=user_document,
                relevance=DocumentContextRelevance.USER,
            ),
            DocumentContextMatch(
                document=project_document,
                relevance=DocumentContextRelevance.PROJECT,
            ),
        ),
    )

    assert result.ordered_documents() == (
        project_document,
        user_document,
    )


def test_document_query_result_ordered_documents_without_matches_preserves_order():
    first = Document.create(
        name="Primero",
        mime_type="text/plain",
        source="first.txt",
    )

    second = Document.create(
        name="Segundo",
        mime_type="text/plain",
        source="second.txt",
    )

    result = DocumentQueryResult.from_documents(
        (
            first,
            second,
        ),
    )

    assert result.ordered_documents() == (
        first,
        second,
    )

def test_document_query_result_ordered_matches_uses_relevance():
    from documents.context_relevance import (
        DocumentContextMatch,
        DocumentContextRelevance,
    )

    user_document = Document.create(
        name="Usuario",
        mime_type="text/plain",
        source="user.txt",
    )

    project_document = Document.create(
        name="Proyecto",
        mime_type="text/plain",
        source="project.txt",
    )

    result = DocumentQueryResult.from_documents(
        (
            user_document,
            project_document,
        ),
        matches=(
            DocumentContextMatch(
                document=user_document,
                relevance=DocumentContextRelevance.USER,
            ),
            DocumentContextMatch(
                document=project_document,
                relevance=DocumentContextRelevance.PROJECT,
            ),
        ),
    )

    assert result.ordered_matches() == (
        DocumentContextMatch(
            document=project_document,
            relevance=DocumentContextRelevance.PROJECT,
        ),
        DocumentContextMatch(
            document=user_document,
            relevance=DocumentContextRelevance.USER,
        ),
    )


def test_document_query_result_ordered_matches_without_matches_returns_empty():
    result = DocumentQueryResult(
        documents=(),
        total=0,
    )

    assert result.ordered_matches() == ()

def test_document_query_result_supports_pagination_metadata():
    document = Document.create(
        name="Documento",
        mime_type="text/plain",
        source="document.txt",
    )

    result = DocumentQueryResult.from_documents(
        (document,),
        total=5,
        offset=2,
        limit=1,
    )

    assert result.documents == (
        document,
    )

    assert result.total == 5
    assert result.offset == 2
    assert result.limit == 1
    assert result.has_more is True


def test_document_query_result_reports_no_more_pages():
    document = Document.create(
        name="Documento",
        mime_type="text/plain",
        source="document.txt",
    )

    result = DocumentQueryResult.from_documents(
        (document,),
        total=3,
        offset=2,
        limit=1,
    )

    assert result.has_more is False


def test_document_query_result_rejects_negative_offset():
    try:
        DocumentQueryResult.from_documents(
            (),
            offset=-1,
        )
    except ValueError:
        pass
    else:
        raise AssertionError(
            "negative offset should be rejected"
        )


def test_document_query_result_rejects_negative_limit():
    try:
        DocumentQueryResult.from_documents(
            (),
            limit=-1,
        )
    except ValueError:
        pass
    else:
        raise AssertionError(
            "negative limit should be rejected"
        )
