import pytest

from documents import (
    DocumentChange,
    DocumentChangeType,
    DocumentSemanticChange,
)


def build_source_change() -> DocumentChange:
    return DocumentChange.modified(
        before="El contrato tiene vigencia de 12 meses.",
        after="El contrato tiene vigencia de 24 meses.",
        before_line=1,
        after_line=1,
    )


def test_semantic_change_preserves_source_change():
    source_change = build_source_change()

    result = DocumentSemanticChange(
        source_change=source_change,
        meaning="La vigencia contractual fue modificada.",
    )

    assert result.source_change == source_change
    assert result.source_change.change_type == (
        DocumentChangeType.MODIFIED
    )


def test_semantic_change_requires_meaning():
    source_change = build_source_change()

    with pytest.raises(
        ValueError,
        match="Semantic change meaning cannot be empty",
    ):
        DocumentSemanticChange(
            source_change=source_change,
            meaning="   ",
        )


def test_semantic_change_accepts_topics():
    source_change = build_source_change()

    result = DocumentSemanticChange(
        source_change=source_change,
        meaning="La vigencia contractual fue modificada.",
        topics=(" contrato ", "vigencia", " "),
    )

    assert result.topics == (
        "contrato",
        "vigencia",
    )


def test_semantic_change_accepts_impact():
    source_change = build_source_change()

    result = DocumentSemanticChange(
        source_change=source_change,
        meaning="La vigencia contractual fue modificada.",
        impact="Requiere revisión contractual.",
    )

    assert result.impact == (
        "Requiere revisión contractual."
    )


def test_semantic_change_normalizes_empty_impact():
    source_change = build_source_change()

    result = DocumentSemanticChange(
        source_change=source_change,
        meaning="La vigencia contractual fue modificada.",
        impact="   ",
    )

    assert result.impact is None


def test_semantic_change_accepts_confidence():
    source_change = build_source_change()

    result = DocumentSemanticChange(
        source_change=source_change,
        meaning="La vigencia contractual fue modificada.",
        confidence=0.92,
    )

    assert result.confidence == 0.92


@pytest.mark.parametrize(
    "confidence",
    [-0.01, 1.01],
)
def test_semantic_change_rejects_invalid_confidence(
    confidence,
):
    source_change = build_source_change()

    with pytest.raises(
        ValueError,
        match="Semantic change confidence must be between 0 and 1",
    ):
        DocumentSemanticChange(
            source_change=source_change,
            meaning="La vigencia contractual fue modificada.",
            confidence=confidence,
        )


def test_semantic_change_accepts_boundary_confidence_values():
    source_change = build_source_change()

    low = DocumentSemanticChange(
        source_change=source_change,
        meaning="Cambio detectado.",
        confidence=0.0,
    )

    high = DocumentSemanticChange(
        source_change=source_change,
        meaning="Cambio detectado.",
        confidence=1.0,
    )

    assert low.confidence == 0.0
    assert high.confidence == 1.0


def test_semantic_change_is_immutable():
    source_change = build_source_change()

    result = DocumentSemanticChange(
        source_change=source_change,
        meaning="La vigencia contractual fue modificada.",
    )

    with pytest.raises(AttributeError):
        result.meaning = "Otro significado"
