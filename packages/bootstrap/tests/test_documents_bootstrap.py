from bootstrap.bootstrap import (
    build_document_services,
    build_engine,
)

from documents import (
    DocumentCapability,
    DocumentCognitiveAccess,
    DocumentServices,
)


def test_bootstrap_builds_document_services():
    services = build_document_services()

    assert isinstance(services, DocumentServices)


def test_bootstrap_document_services_are_composed():
    services = build_document_services()

    assert services.document_store is not None
    assert services.artifact_store is not None
    assert services.content_store is not None
    assert services.ingestion_registry is not None
    assert services.ingestion_service is not None
    assert services.document_service is not None


def test_bootstrap_injects_document_capability_into_engine():
    engine = build_engine()

    assert isinstance(
        engine.document_capability,
        DocumentCapability,
    )

    assert (
        engine.document_capability.context_access
        is not None
    )


def test_bootstrap_injects_document_cognitive_access_into_engine():
    engine = build_engine()

    assert isinstance(
        engine.document_cognitive_access,
        DocumentCognitiveAccess,
    )
