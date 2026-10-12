from documents import (
    DocumentChangeDetector,
    DocumentChangeType,
    DocumentContentVersion,
    DocumentContentVersionStore,
    DocumentVersionComparator,
    DocumentVersionResolver,
)


def add_version(
    store: DocumentContentVersionStore,
    document_id: str,
    version: int,
    content_id: str,
) -> DocumentContentVersion:
    content_version = DocumentContentVersion.create(
        document_id=document_id,
        content_id=content_id,
        version=version,
        content_type="text/plain",
    )
    store.add(content_version)
    return content_version


def build_comparison(
    document_id: str = "doc-1",
    from_content_id: str = "content-1",
    to_content_id: str = "content-2",
):
    store = DocumentContentVersionStore()

    add_version(
        store,
        document_id=document_id,
        version=1,
        content_id=from_content_id,
    )

    add_version(
        store,
        document_id=document_id,
        version=2,
        content_id=to_content_id,
    )

    resolver = DocumentVersionResolver(store)
    resolution = resolver.resolve_pair(
        document_id=document_id,
        from_version=1,
        to_version=2,
    )

    return DocumentVersionComparator().compare(resolution)


def test_detector_detects_modified_line():
    comparison = build_comparison()

    detector = DocumentChangeDetector()

    result = detector.detect(
        comparison,
        before_text="El contrato tiene vigencia de 12 meses.",
        after_text="El contrato tiene vigencia de 24 meses.",
    )

    assert result.changed is True
    assert result.unchanged is False
    assert len(result.changes) == 1

    change = result.changes[0]

    assert change.change_type == DocumentChangeType.MODIFIED
    assert change.before == "El contrato tiene vigencia de 12 meses."
    assert change.after == "El contrato tiene vigencia de 24 meses."
    assert change.before_line == 1
    assert change.after_line == 1


def test_detector_detects_added_line():
    comparison = build_comparison()

    detector = DocumentChangeDetector()

    result = detector.detect(
        comparison,
        before_text="Primera línea.",
        after_text="Primera línea.\nSegunda línea.",
    )

    assert result.changed is True
    assert len(result.changes) == 1

    change = result.changes[0]

    assert change.change_type == DocumentChangeType.ADDED
    assert change.before is None
    assert change.after == "Segunda línea."
    assert change.after_line == 2


def test_detector_detects_removed_line():
    comparison = build_comparison()

    detector = DocumentChangeDetector()

    result = detector.detect(
        comparison,
        before_text="Primera línea.\nSegunda línea.",
        after_text="Primera línea.",
    )

    assert result.changed is True
    assert len(result.changes) == 1

    change = result.changes[0]

    assert change.change_type == DocumentChangeType.REMOVED
    assert change.before == "Segunda línea."
    assert change.after is None
    assert change.before_line == 2


def test_detector_detects_multiple_changes():
    comparison = build_comparison()

    detector = DocumentChangeDetector()

    result = detector.detect(
        comparison,
        before_text="A\nB\nC",
        after_text="A\nX\nC\nD",
    )

    assert len(result.changes) == 2

    modified = result.changes[0]
    added = result.changes[1]

    assert modified.change_type == DocumentChangeType.MODIFIED
    assert modified.before == "B"
    assert modified.after == "X"
    assert modified.before_line == 2
    assert modified.after_line == 2

    assert added.change_type == DocumentChangeType.ADDED
    assert added.after == "D"
    assert added.after_line == 4


def test_detector_returns_no_changes_for_identical_text():
    comparison = build_comparison(
        from_content_id="content-1",
        to_content_id="content-1",
    )

    detector = DocumentChangeDetector()

    result = detector.detect(
        comparison,
        before_text="A\nB\nC",
        after_text="A\nB\nC",
    )

    assert result.changed is False
    assert result.unchanged is True
    assert result.changes == ()


def test_detector_preserves_comparison():
    comparison = build_comparison()

    detector = DocumentChangeDetector()

    result = detector.detect(
        comparison,
        before_text="Antes",
        after_text="Después",
    )

    assert result.comparison == comparison


def test_detector_returns_immutable_changes():
    comparison = build_comparison()

    detector = DocumentChangeDetector()

    result = detector.detect(
        comparison,
        before_text="Antes",
        after_text="Después",
    )

    assert isinstance(result.changes, tuple)
