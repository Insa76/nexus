import pytest

from documents import (
    ArtifactTypeResolver,
    DocumentArtifact,
    DocumentType,
    ExtensionTypeDetectionStrategy,
    DeclaredTypeDetectionStrategy,
)


def test_extension_strategy_resolves_txt():
    strategy = ExtensionTypeDetectionStrategy()

    artifact = DocumentArtifact.create(
        location="C:/documents/manual.txt",
    )

    result = strategy.resolve(artifact)

    assert result is not None
    assert result.mime_type == "text/plain"


def test_extension_strategy_returns_none_for_unknown_extension():
    strategy = ExtensionTypeDetectionStrategy()

    artifact = DocumentArtifact.create(
        location="C:/documents/manual.xyz",
    )

    result = strategy.resolve(artifact)

    assert result is None


def test_extension_strategy_returns_none_for_empty_location():
    strategy = ExtensionTypeDetectionStrategy()

    artifact = DocumentArtifact.create(
        location="   ",
    )

    result = strategy.resolve(artifact)

    assert result is None


def test_resolver_uses_registered_strategy():
    class FakeStrategy:
        def resolve(self, artifact):
            return DocumentType.from_mime_type(
                "application/custom"
            )

    resolver = ArtifactTypeResolver(
        strategies=[FakeStrategy()]
    )

    artifact = DocumentArtifact.create(
        location="C:/documents/unknown.xyz",
    )

    result = resolver.resolve(artifact)

    assert result.mime_type == "application/custom"


def test_resolver_uses_strategies_in_order():
    calls = []

    class FirstStrategy:
        def resolve(self, artifact):
            calls.append("first")
            return None

    class SecondStrategy:
        def resolve(self, artifact):
            calls.append("second")
            return DocumentType.from_mime_type(
                "application/custom"
            )

    resolver = ArtifactTypeResolver(
        strategies=[
            FirstStrategy(),
            SecondStrategy(),
        ]
    )

    artifact = DocumentArtifact.create(
        location="C:/documents/unknown.xyz",
    )

    result = resolver.resolve(artifact)

    assert result.mime_type == "application/custom"
    assert calls == [
        "first",
        "second",
    ]


def test_resolver_stops_after_successful_strategy():
    calls = []

    class FirstStrategy:
        def resolve(self, artifact):
            calls.append("first")
            return DocumentType.from_mime_type(
                "text/plain"
            )

    class SecondStrategy:
        def resolve(self, artifact):
            calls.append("second")
            return DocumentType.from_mime_type(
                "application/pdf"
            )

    resolver = ArtifactTypeResolver(
        strategies=[
            FirstStrategy(),
            SecondStrategy(),
        ]
    )

    artifact = DocumentArtifact.create(
        location="C:/documents/manual.txt",
    )

    result = resolver.resolve(artifact)

    assert result.mime_type == "text/plain"
    assert calls == ["first"]


def test_resolver_rejects_unresolved_artifact():
    resolver = ArtifactTypeResolver(
        strategies=[]
    )

    artifact = DocumentArtifact.create(
        location="C:/documents/manual.xyz",
    )

    with pytest.raises(
        ValueError,
        match="Cannot resolve document type",
    ):
        resolver.resolve(artifact)

def test_resolver_prefers_declared_type_over_extension():
    from documents import DeclaredTypeDetectionStrategy

    declared_strategy = DeclaredTypeDetectionStrategy()

    artifact = DocumentArtifact.create(
        location="C:/documents/manual.txt",
    )

    declared_strategy.declare(
        artifact,
        "application/pdf",
    )

    resolver = ArtifactTypeResolver(
        strategies=[
            declared_strategy,
            ExtensionTypeDetectionStrategy(),
        ]
    )

    result = resolver.resolve(
        artifact
    )

    assert result.mime_type == "application/pdf"


def test_default_resolver_contains_declared_and_extension_strategies():
    resolver = ArtifactTypeResolver()

    strategies = resolver.strategies()

    assert len(strategies) == 2
    assert isinstance(
        strategies[0],
        DeclaredTypeDetectionStrategy,
    )
    assert isinstance(
        strategies[1],
        ExtensionTypeDetectionStrategy,
    )
