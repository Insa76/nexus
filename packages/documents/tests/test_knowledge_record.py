from documents import (
    DocumentChange,
    DocumentKnowledge,
    DocumentKnowledgeRecord,
    DocumentSemanticChange,
)


def build_knowledge() -> DocumentKnowledge:
    change = DocumentChange.modified(
        "Vigencia: 12 meses.",
        "Vigencia: 24 meses.",
        before_line=1,
        after_line=1,
    )

    semantic_change = DocumentSemanticChange(
        source_change=change,
        meaning="Se modificó la vigencia.",
        topics=("vigencia",),
        confidence=0.9,
    )

    return DocumentKnowledge(
        source_change=semantic_change,
        statement=(
            "La vigencia indicada en el documento "
            "pasó de 12 meses a 24 meses."
        ),
        topic="vigencia",
        confidence=0.9,
    )


def test_knowledge_record_create():
    knowledge = build_knowledge()

    record = DocumentKnowledgeRecord.create(
        document_id="doc-1",
        content_version_id="version-2",
        knowledge=knowledge,
    )

    assert record.id
    assert record.document_id == "doc-1"
    assert record.content_version_id == "version-2"
    assert record.knowledge == knowledge
    assert record.created_at is not None


def test_knowledge_record_preserves_knowledge():
    knowledge = build_knowledge()

    record = DocumentKnowledgeRecord.create(
        document_id="doc-1",
        content_version_id="version-2",
        knowledge=knowledge,
    )

    assert record.knowledge.statement == (
        "La vigencia indicada en el documento "
        "pasó de 12 meses a 24 meses."
    )


def test_knowledge_record_preserves_source_change():
    knowledge = build_knowledge()

    record = DocumentKnowledgeRecord.create(
        document_id="doc-1",
        content_version_id="version-2",
        knowledge=knowledge,
    )

    semantic_change = record.knowledge.source_change
    deterministic_change = semantic_change.source_change

    assert deterministic_change.before == "Vigencia: 12 meses."
    assert deterministic_change.after == "Vigencia: 24 meses."


def test_knowledge_record_generates_unique_ids():
    knowledge = build_knowledge()

    first = DocumentKnowledgeRecord.create(
        document_id="doc-1",
        content_version_id="version-2",
        knowledge=knowledge,
    )

    second = DocumentKnowledgeRecord.create(
        document_id="doc-1",
        content_version_id="version-2",
        knowledge=knowledge,
    )

    assert first.id != second.id


def test_knowledge_record_is_immutable():
    knowledge = build_knowledge()

    record = DocumentKnowledgeRecord.create(
        document_id="doc-1",
        content_version_id="version-2",
        knowledge=knowledge,
    )

    try:
        record.document_id = "doc-2"
    except AttributeError:
        pass
    else:
        raise AssertionError(
            "DocumentKnowledgeRecord must be immutable"
        )


def test_knowledge_record_has_creation_timestamp():
    knowledge = build_knowledge()

    record = DocumentKnowledgeRecord.create(
        document_id="doc-1",
        content_version_id="version-2",
        knowledge=knowledge,
    )

    assert record.created_at.tzinfo is not None
