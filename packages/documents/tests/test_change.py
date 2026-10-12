from documents import DocumentChange, DocumentChangeType


def test_added_change():
    change = DocumentChange.added(
        "Nueva línea",
        line=3,
    )

    assert change.change_type == DocumentChangeType.ADDED
    assert change.before is None
    assert change.after == "Nueva línea"
    assert change.before_line is None
    assert change.after_line == 3


def test_removed_change():
    change = DocumentChange.removed(
        "Línea eliminada",
        line=4,
    )

    assert change.change_type == DocumentChangeType.REMOVED
    assert change.before == "Línea eliminada"
    assert change.after is None
    assert change.before_line == 4
    assert change.after_line is None


def test_modified_change():
    change = DocumentChange.modified(
        "12 meses",
        "24 meses",
        before_line=2,
        after_line=2,
    )

    assert change.change_type == DocumentChangeType.MODIFIED
    assert change.before == "12 meses"
    assert change.after == "24 meses"
    assert change.before_line == 2
    assert change.after_line == 2
