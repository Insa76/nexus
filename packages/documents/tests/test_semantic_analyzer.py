from documents import (
    DocumentChange,
    DocumentSemanticAnalyzer,
    RuleBasedSemanticAnalyzer,
)


def test_rule_based_analyzer_implements_semantic_analyzer():
    analyzer = RuleBasedSemanticAnalyzer()

    assert isinstance(analyzer, DocumentSemanticAnalyzer)


def test_rule_based_analyzer_analyzes_added_change():
    change = DocumentChange.added(
        "Nueva cláusula.",
        line=3,
    )

    analyzer = RuleBasedSemanticAnalyzer()

    result = analyzer.analyze(change)

    assert result.source_change == change
    assert result.meaning == (
        "Se agregó contenido al documento."
    )
    assert result.confidence == 1.0


def test_rule_based_analyzer_analyzes_removed_change():
    change = DocumentChange.removed(
        "Cláusula eliminada.",
        line=4,
    )

    analyzer = RuleBasedSemanticAnalyzer()

    result = analyzer.analyze(change)

    assert result.source_change == change
    assert result.meaning == (
        "Se eliminó contenido del documento."
    )
    assert result.confidence == 1.0


def test_rule_based_analyzer_analyzes_modified_change():
    change = DocumentChange.modified(
        "Vigencia: 12 meses.",
        "Vigencia: 24 meses.",
        before_line=2,
        after_line=2,
    )

    analyzer = RuleBasedSemanticAnalyzer()

    result = analyzer.analyze(change)

    assert result.source_change == change
    assert result.meaning == (
        "Se modificó contenido existente del documento."
    )
    assert result.confidence == 1.0


def test_rule_based_analyzer_preserves_change_evidence():
    change = DocumentChange.modified(
        "Antes",
        "Después",
        before_line=5,
        after_line=5,
    )

    result = RuleBasedSemanticAnalyzer().analyze(change)

    assert result.source_change.before == "Antes"
    assert result.source_change.after == "Después"
    assert result.source_change.before_line == 5
    assert result.source_change.after_line == 5
