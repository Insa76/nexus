from documents import (
    DocumentChange,
    DocumentKnowledge,
    DocumentSemanticChange,
)


def build_semantic_change() -> DocumentSemanticChange:
    change = DocumentChange.modified(
        "Vigencia: 12 meses.",
        "Vigencia: 24 meses.",
        before_line=1,
        after_line=1,
    )

    return DocumentSemanticChange(
        source_change=change,
        meaning="Se modificó la vigencia.",
        topics=("vigencia",),
        confidence=0.9,
    )


def test_document_knowledge_preserves_source_change():
    semantic_change = build_semantic_change()

    knowledge = DocumentKnowledge(
        source_change=semantic_change,
        statement=(
            "La vigencia indicada en el documento "
            "pasó de 12 meses a 24 meses."
        ),
    )

    assert knowledge.source_change == semantic_change


def test_document_knowledge_stores_statement():
    knowledge = DocumentKnowledge(
        source_change=build_semantic_change(),
        statement="La vigencia indicada cambió.",
    )

    assert knowledge.statement == (
        "La vigencia indicada cambió."
    )


def test_document_knowledge_stores_topic():
    knowledge = DocumentKnowledge(
        source_change=build_semantic_change(),
        statement="La vigencia indicada cambió.",
        topic=" vigencia ",
    )

    assert knowledge.topic == "vigencia"


def test_document_knowledge_normalizes_empty_topic():
    knowledge = DocumentKnowledge(
        source_change=build_semantic_change(),
        statement="La vigencia indicada cambió.",
        topic="   ",
    )

    assert knowledge.topic is None


def test_document_knowledge_accepts_confidence():
    knowledge = DocumentKnowledge(
        source_change=build_semantic_change(),
        statement="La vigencia indicada cambió.",
        confidence=0.85,
    )

    assert knowledge.confidence == 0.85


def test_document_knowledge_rejects_invalid_confidence():
    try:
        DocumentKnowledge(
            source_change=build_semantic_change(),
            statement="La vigencia indicada cambió.",
            confidence=1.1,
        )
    except ValueError as exc:
        assert str(exc) == (
            "Document knowledge confidence must be between 0 and 1"
        )
    else:
        raise AssertionError(
            "Expected ValueError for invalid confidence"
        )


def test_document_knowledge_rejects_empty_statement():
    try:
        DocumentKnowledge(
            source_change=build_semantic_change(),
            statement="   ",
        )
    except ValueError as exc:
        assert str(exc) == (
            "Document knowledge statement cannot be empty"
        )
    else:
        raise AssertionError(
            "Expected ValueError for empty statement"
        )


def test_document_knowledge_is_immutable():
    knowledge = DocumentKnowledge(
        source_change=build_semantic_change(),
        statement="La vigencia indicada cambió.",
    )

    try:
        knowledge.statement = "Otro conocimiento."
    except AttributeError:
        pass
    else:
        raise AssertionError(
            "DocumentKnowledge must be immutable"
        )
