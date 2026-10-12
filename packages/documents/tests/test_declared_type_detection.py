from documents import (
    DeclaredTypeDetectionStrategy,
    DocumentArtifact,
)


def test_declared_type_strategy_resolves_declared_type():
    artifact = DocumentArtifact.create(
        location="C:/documents/manual.txt",
    )

    strategy = DeclaredTypeDetectionStrategy()

    strategy.declare(
        artifact,
        "application/pdf",
    )

    result = strategy.resolve(
        artifact
    )

    assert result is not None
    assert result.mime_type == "application/pdf"


def test_declared_type_strategy_returns_none_when_not_declared():
    artifact = DocumentArtifact.create(
        location="C:/documents/manual.txt",
    )

    strategy = DeclaredTypeDetectionStrategy()

    result = strategy.resolve(
        artifact
    )

    assert result is None


def test_declared_type_strategy_normalizes_mime_type():
    artifact = DocumentArtifact.create(
        location="C:/documents/manual.txt",
    )

    strategy = DeclaredTypeDetectionStrategy()

    strategy.declare(
        artifact,
        " APPLICATION/PDF ",
    )

    result = strategy.resolve(
        artifact
    )

    assert result is not None
    assert result.mime_type == "application/pdf"


def test_declared_type_strategy_can_remove_declaration():
    artifact = DocumentArtifact.create(
        location="C:/documents/manual.txt",
    )

    strategy = DeclaredTypeDetectionStrategy()

    strategy.declare(
        artifact,
        "application/pdf",
    )

    removed = strategy.remove(
        artifact
    )

    assert removed == "application/pdf"
    assert strategy.resolve(
        artifact
    ) is None


def test_declared_type_strategy_remove_unknown_returns_none():
    artifact = DocumentArtifact.create(
        location="C:/documents/manual.txt",
    )

    strategy = DeclaredTypeDetectionStrategy()

    assert strategy.remove(
        artifact
    ) is None
