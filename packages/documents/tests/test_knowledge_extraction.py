from documents import (
    DocumentChange,
    DocumentKnowledge,
    DocumentKnowledgeExtraction,
    DocumentSemanticAnalysis,
    DocumentSemanticChange,
    DocumentVersionChangeResult,
    DocumentVersionComparison,
)


def build_analysis() -> DocumentSemanticAnalysis:
    comparison = DocumentVersionComparison(
        document_id="doc-1",
        from_version=1,
        to_version=2,
        from_content_id="content-1",
        to_content_id="content-2",
        changed=True,
    )

    source_result = DocumentVersionChangeResult(
        comparison=comparison,
        changes=(
            DocumentChange.modified(
                "Vigencia: 12 meses.",
                "Vigencia: 24 meses.",
                before_line=1,
                after_line=1,
            ),
            DocumentChange.added(
                "Nueva cláusula.",
                line=3,
            ),
        ),
    )

    semantic_changes = (
        DocumentSemanticChange(
            source_change=source_result.changes[0],
            meaning="Se modificó la vigencia.",
            topics=("vigencia",),
            confidence=0.9,
        ),
        DocumentSemanticChange(
            source_change=source_result.changes[1],
            meaning="Se agregó una nueva cláusula.",
            topics=("contrato",),
            confidence=1.0,
        ),
    )

    return DocumentSemanticAnalysis(
        source=source_result,
        changes=semantic_changes,
    )


class FakeKnowledgeExtractor:
    def extract(
        self,
        change: DocumentSemanticChange,
    ) -> tuple[DocumentKnowledge, ...]:
        return (
            DocumentKnowledge(
                source_change=change,
                statement=change.meaning,
                topic=change.topics[0] if change.topics else None,
                confidence=change.confidence,
            ),
        )


def test_knowledge_extraction_preserves_source_analysis():
    analysis = build_analysis()

    extraction = DocumentKnowledgeExtraction(
        source=analysis,
        knowledge=(),
    )

    assert extraction.source == analysis


def test_knowledge_extraction_contains_knowledge():
    analysis = build_analysis()

    knowledge = (
        DocumentKnowledge(
            source_change=analysis.changes[0],
            statement="Se modificó la vigencia.",
        ),
    )

    extraction = DocumentKnowledgeExtraction(
        source=analysis,
        knowledge=knowledge,
    )

    assert len(extraction.knowledge) == 1
    assert extraction.knowledge[0].statement == (
        "Se modificó la vigencia."
    )


def test_knowledge_extraction_extracted_is_true():
    analysis = build_analysis()

    extraction = DocumentKnowledgeExtraction(
        source=analysis,
        knowledge=(
            DocumentKnowledge(
                source_change=analysis.changes[0],
                statement="Se modificó la vigencia.",
            ),
        ),
    )

    assert extraction.extracted is True
    assert extraction.empty is False


def test_knowledge_extraction_empty_when_no_knowledge():
    extraction = DocumentKnowledgeExtraction(
        source=build_analysis(),
        knowledge=(),
    )

    assert extraction.extracted is False
    assert extraction.empty is True


def test_knowledge_extraction_is_immutable():
    extraction = DocumentKnowledgeExtraction(
        source=build_analysis(),
        knowledge=(),
    )

    assert isinstance(extraction.knowledge, tuple)


def test_service_extracts_all_semantic_changes():
    from documents import DocumentKnowledgeExtractionService

    service = DocumentKnowledgeExtractionService(
        extractor=FakeKnowledgeExtractor(),
    )

    analysis = build_analysis()

    extraction = service.extract(analysis)

    assert len(extraction.knowledge) == 2


def test_service_preserves_change_order():
    from documents import DocumentKnowledgeExtractionService

    service = DocumentKnowledgeExtractionService(
        extractor=FakeKnowledgeExtractor(),
    )

    analysis = build_analysis()

    extraction = service.extract(analysis)

    assert (
        extraction.knowledge[0].source_change
        == analysis.changes[0]
    )

    assert (
        extraction.knowledge[1].source_change
        == analysis.changes[1]
    )

    assert (
        extraction.knowledge[0].source_change.source_change
        == analysis.changes[0].source_change
    )

    assert (
        extraction.knowledge[1].source_change.source_change
        == analysis.changes[1].source_change
    )


def test_service_returns_empty_extraction_without_changes():
    from documents import DocumentKnowledgeExtractionService

    comparison = DocumentVersionComparison(
        document_id="doc-1",
        from_version=1,
        to_version=2,
        from_content_id="content-1",
        to_content_id="content-2",
        changed=False,
    )

    source = DocumentVersionChangeResult(
        comparison=comparison,
        changes=(),
    )

    analysis = DocumentSemanticAnalysis(
        source=source,
        changes=(),
    )

    service = DocumentKnowledgeExtractionService(
        extractor=FakeKnowledgeExtractor(),
    )

    extraction = service.extract(analysis)

    assert extraction.knowledge == ()
    assert extraction.extracted is False
    assert extraction.empty is True
