from documents import (
    DocumentChange,
    DocumentSemanticAnalysisService,
    DocumentSemanticAnalyzer,
    DocumentSemanticChange,
    DocumentVersionChangeResult,
    DocumentVersionComparison,
    RuleBasedSemanticAnalyzer,
)


def build_result() -> DocumentVersionChangeResult:
    comparison = DocumentVersionComparison(
        document_id="doc-1",
        from_version=1,
        to_version=2,
        from_content_id="content-1",
        to_content_id="content-2",
        changed=True,
    )

    changes = (
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
    )

    return DocumentVersionChangeResult(
        comparison=comparison,
        changes=changes,
    )


class FakeSemanticAnalyzer:
    def analyze(
        self,
        change: DocumentChange,
    ) -> DocumentSemanticChange:
        return DocumentSemanticChange(
            source_change=change,
            meaning="Cambio analizado.",
            confidence=0.75,
        )


def test_service_accepts_semantic_analyzer():
    analyzer = FakeSemanticAnalyzer()

    service = DocumentSemanticAnalysisService(
        analyzer=analyzer,
    )

    assert isinstance(
        service.analyzer,
        DocumentSemanticAnalyzer,
    )


def test_service_analyzes_all_changes():
    service = DocumentSemanticAnalysisService(
        analyzer=FakeSemanticAnalyzer(),
    )

    result = build_result()

    analysis = service.analyze(result)

    assert len(analysis.changes) == 2

    assert all(
        change.meaning == "Cambio analizado."
        for change in analysis.changes
    )


def test_service_preserves_source_result():
    service = DocumentSemanticAnalysisService(
        analyzer=FakeSemanticAnalyzer(),
    )

    result = build_result()

    analysis = service.analyze(result)

    assert analysis.source == result


def test_service_preserves_change_order():
    service = DocumentSemanticAnalysisService(
        analyzer=FakeSemanticAnalyzer(),
    )

    result = build_result()

    analysis = service.analyze(result)

    assert (
        analysis.changes[0].source_change
        == result.changes[0]
    )

    assert (
        analysis.changes[1].source_change
        == result.changes[1]
    )


def test_service_with_rule_based_analyzer():
    service = DocumentSemanticAnalysisService(
        analyzer=RuleBasedSemanticAnalyzer(),
    )

    analysis = service.analyze(build_result())

    assert len(analysis.changes) == 2

    assert (
        analysis.changes[0].meaning
        == "Se modificó contenido existente del documento."
    )

    assert (
        analysis.changes[1].meaning
        == "Se agregó contenido al documento."
    )


def test_service_returns_unchanged_analysis_when_no_changes():
    comparison = DocumentVersionComparison(
        document_id="doc-1",
        from_version=1,
        to_version=2,
        from_content_id="content-1",
        to_content_id="content-2",
        changed=False,
    )

    result = DocumentVersionChangeResult(
        comparison=comparison,
        changes=(),
    )

    service = DocumentSemanticAnalysisService(
        analyzer=FakeSemanticAnalyzer(),
    )

    analysis = service.analyze(result)

    assert analysis.changes == ()
    assert analysis.changed is False
    assert analysis.unchanged is True
