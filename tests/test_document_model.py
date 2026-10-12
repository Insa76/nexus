from datetime import timezone

from documents import Document


def test_document_create() -> None:
    document = Document.create(
        name="Contrato.pdf",
        mime_type="application/pdf",
        source="local:/documents/contrato.pdf",
    )

    assert document.id
    assert document.name == "Contrato.pdf"
    assert document.mime_type == "application/pdf"
    assert document.source == "local:/documents/contrato.pdf"
    assert document.description is None
    assert document.user_id is None
    assert document.organization_id is None
    assert document.project_id is None
    assert document.metadata == {}
    assert document.created_at.tzinfo == timezone.utc
    assert document.updated_at.tzinfo == timezone.utc


def test_document_create_with_context_and_metadata() -> None:
    document = Document.create(
        name="Informe.pdf",
        mime_type="application/pdf",
        source="local:/documents/informe.pdf",
        description="Informe mensual",
        user_id="user-1",
        organization_id="org-1",
        project_id="project-1",
        metadata={
            "department": "finance",
            "year": "2026",
        },
    )

    assert document.description == "Informe mensual"
    assert document.user_id == "user-1"
    assert document.organization_id == "org-1"
    assert document.project_id == "project-1"
    assert document.metadata == {
        "department": "finance",
        "year": "2026",
    }


def test_document_is_immutable() -> None:
    document = Document.create(
        name="Documento.txt",
        mime_type="text/plain",
        source="memory:test",
    )

    try:
        document.name = "Otro.txt"
    except AttributeError:
        pass
    else:
        raise AssertionError(
            "Document should be immutable"
        )


def test_document_create_copies_metadata() -> None:
    metadata = {
        "category": "legal",
    }

    document = Document.create(
        name="Contrato.txt",
        mime_type="text/plain",
        source="local:/documents/contrato.txt",
        metadata=metadata,
    )

    metadata["category"] = "finance"

    assert document.metadata == {
        "category": "legal",
    }
