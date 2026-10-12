from documents import (
    DocumentChange,
    DocumentSemanticAnalysis,
    DocumentSemanticChange,
    DocumentVersionChangeResult,
    DocumentVersionComparison,
)


def build_comparison() -> DocumentVersionComparison:
    return DocumentVersionComparison(
        document_id="doc-1",
        from_version=1,
        to_version=2,
        from_content_id="content-1",
        to_content_id="content-2",
        changed=True,
    )


def build_source_result() -> DocumentVersionChangeResult:
    change = DocumentChange.modified(
        "Vigencia: 12 meses.",
        "Vigencia: 24 meses.",
        before_line=1,
        after_line=1,
    )

    return DocumentVersionChangeResult(
        comparison=build_comparison(),
        changes=(change,),
    )


def build_semantic_change() -> DocumentSemanticChange:
    source = build_source_result().changes[0]

    return DocumentSemanticChange(
        source_change=source,
        meaning="Se modificó la vigencia.",
        topics=("vigencia",),
        confidence=0.9,
    )


def test_semantic_analysis_preserves_source_result():
    source = build_source_result()

    analysis = DocumentSemanticAnalysis(
        source=source,
        changes=(build_semantic_change(),),
    )

    assert analysis.source == source


def test_semantic_analysis_contains_semantic_changes():
    analysis = DocumentSemanticAnalysis(
        source=build_source_result(),
        changes=(build_semantic_change(),),
    )

    assert len(analysis.changes) == 1
    assert analysis.changes[0].meaning == (
        "Se modificó la vigencia."
    )


def test_semantic_analysis_changed_is_true_when_changes_exist():
    analysis = DocumentSemanticAnalysis(
        source=build_source_result(),
        changes=(build_semantic_change(),),
    )

    assert analysis.changed is True
    assert analysis.unchanged is False


def test_semantic_analysis_unchanged_when_no_semantic_changes():
    analysis = DocumentSemanticAnalysis(
        source=build_source_result(),
        changes=(),
    )

    assert analysis.changed is False
    assert analysis.unchanged is True


def test_semantic_analysis_changes_are_immutable():
    analysis = DocumentSemanticAnalysis(
        source=build_source_result(),
        changes=(build_semantic_change(),),
    )

    assert isinstance(analysis.changes, tuple)
