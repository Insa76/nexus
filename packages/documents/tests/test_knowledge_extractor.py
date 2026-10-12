from documents import (
    DocumentChange,
    DocumentKnowledge,
    DocumentKnowledgeExtractor,
    DocumentSemanticChange,
    RuleBasedDocumentKnowledgeExtractor,
)


def build_change() -> DocumentSemanticChange:
    change = DocumentChange.modified(
        "Vigencia: 12 meses.",
        "Vigencia: 24 meses.",
        before_line=1,
        after_line=1,
    )

    return DocumentSemanticChange(
        source_change=change,
        meaning="Se modificó la vigencia.",
        topics=("vigencia", "contrato"),
        confidence=0.9,
    )


def test_rule_based_extractor_implements_contract():
    extractor = RuleBasedDocumentKnowledgeExtractor()

    assert isinstance(
        extractor,
        DocumentKnowledgeExtractor,
    )


def test_extractor_returns_tuple():
    extractor = RuleBasedDocumentKnowledgeExtractor()

    result = extractor.extract(build_change())

    assert isinstance(result, tuple)


def test_extractor_creates_knowledge():
    extractor = RuleBasedDocumentKnowledgeExtractor()

    result = extractor.extract(build_change())

    assert len(result) == 1
    assert isinstance(result[0], DocumentKnowledge)


def test_extractor_preserves_semantic_source():
    change = build_change()
    extractor = RuleBasedDocumentKnowledgeExtractor()

    result = extractor.extract(change)

    assert result[0].source_change == change


def test_extractor_uses_semantic_meaning_as_statement():
    extractor = RuleBasedDocumentKnowledgeExtractor()

    result = extractor.extract(build_change())

    assert result[0].statement == (
        "Se modificó la vigencia."
    )


def test_extractor_uses_first_topic():
    extractor = RuleBasedDocumentKnowledgeExtractor()

    result = extractor.extract(build_change())

    assert result[0].topic == "vigencia"


def test_extractor_preserves_confidence():
    extractor = RuleBasedDocumentKnowledgeExtractor()

    result = extractor.extract(build_change())

    assert result[0].confidence == 0.9


def test_extractor_handles_change_without_topics():
    change = DocumentSemanticChange(
        source_change=DocumentChange.added(
            "Nueva cláusula.",
            line=2,
        ),
        meaning="Se agregó contenido al documento.",
        confidence=1.0,
    )

    extractor = RuleBasedDocumentKnowledgeExtractor()

    result = extractor.extract(change)

    assert len(result) == 1
    assert result[0].topic is None
    assert result[0].statement == (
        "Se agregó contenido al documento."
    )
