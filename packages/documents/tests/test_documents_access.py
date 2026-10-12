from documents import (
    Document,
    DocumentArtifact,
    DocumentsAccess,
    DocumentServices,
    build_document_services,
)


def test_document_services_expose_access():
    services = build_document_services()

    assert isinstance(services.access, DocumentsAccess)


def test_access_uses_document_service():
    services = build_document_services()

    assert services.access.service is services.document_service


def test_access_can_create_document():
    services = build_document_services()

    document = services.access.create_document(
        name="test.txt",
        mime_type="text/plain",
        source="local:test.txt",
    )

    assert services.document_store.get(document.id) == document


def test_access_can_add_artifact():
    services = build_document_services()

    artifact = DocumentArtifact.create(
        location="local:test.txt",
    )

    result = services.access.add_artifact(artifact)

    assert result == artifact
    assert services.artifact_store.get(artifact.id) == artifact


def test_access_can_resolve_document():
    services = build_document_services()

    document = services.access.create_document(
        name="test.txt",
        mime_type="text/plain",
        source="local:test.txt",
    )

    result = services.access.resolve(document.id)

    assert result is not None
    assert result.document == document


def test_access_returns_none_for_unknown_document():
    services = build_document_services()

    result = services.access.resolve("missing")

    assert result is None

def test_access_reports_supported_content_types():
    services = build_document_services()

    services.ingestion_registry.register(
        "text/plain",
        object(),
    )

    services.ingestion_registry.register(
        "application/pdf",
        object(),
    )

    assert services.access.supported_content_types() == [
        "text/plain",
        "application/pdf",
    ]

def test_access_can_list_knowledge_history():
    services = build_document_services()

    result = services.access.list_knowledge_history(
        "missing",
    )

    assert result == []

def test_access_can_list_persisted_knowledge_history(tmp_path):
    services = build_document_services()

    source = tmp_path / "document.txt"
    source.write_text(
        "Contenido original.",
        encoding="utf-8",
    )

    artifact = DocumentArtifact.create(
        location=f"local:{source}",
    )

    services.access.add_artifact(artifact)

    document = services.access.create_document(
        name=source.name,
        mime_type="text/plain",
        source=f"local:{source}",
        artifact_id=artifact.id,
    )

    services.document_service.ingest(document)

    source.write_text(
        "Contenido actualizado.",
        encoding="utf-8",
    )

    services.document_service.ingest(document)

    extraction = services.document_service.extract_version_knowledge(
        document_id=document.id,
        from_version=1,
        to_version=2,
    )

    history = services.access.list_knowledge_history(
        document.id,
    )

    assert len(history) == len(extraction.knowledge)

    assert all(
        record.document_id == document.id
        for record in history
    )

    assert [
        record.knowledge
        for record in history
    ] == list(extraction.knowledge)

def test_access_can_list_latest_knowledge_for_document(
    tmp_path,
):
    services = build_document_services()

    source = tmp_path / "document.txt"
    source.write_text(
        "Contenido original.",
        encoding="utf-8",
    )

    artifact = DocumentArtifact.create(
        location=f"local:{source}",
    )

    services.access.add_artifact(artifact)

    document = services.access.create_document(
        name=source.name,
        mime_type="text/plain",
        source=f"local:{source}",
        artifact_id=artifact.id,
    )

    services.document_service.ingest(document)

    source.write_text(
        "Contenido actualizado.",
        encoding="utf-8",
    )

    services.document_service.ingest(document)

    extraction = services.document_service.extract_version_knowledge(
        document_id=document.id,
        from_version=1,
        to_version=2,
    )

    latest = services.access.list_latest_knowledge(
        document.id,
    )

    assert len(latest) == len(extraction.knowledge)

    assert [
        record.knowledge
        for record in latest
    ] == list(extraction.knowledge)

def test_access_can_list_knowledge_for_specific_version(
    tmp_path,
):
    services = build_document_services()

    source = tmp_path / "document.txt"
    source.write_text(
        "Contenido original.",
        encoding="utf-8",
    )

    artifact = DocumentArtifact.create(
        location=f"local:{source}",
    )

    services.access.add_artifact(artifact)

    document = services.access.create_document(
        name=source.name,
        mime_type="text/plain",
        source=f"local:{source}",
        artifact_id=artifact.id,
    )

    services.document_service.ingest(document)

    source.write_text(
        "Contenido actualizado.",
        encoding="utf-8",
    )

    services.document_service.ingest(document)

    extraction = services.document_service.extract_version_knowledge(
        document_id=document.id,
        from_version=1,
        to_version=2,
    )

    result = services.access.list_knowledge_for_version(
        document_id=document.id,
        version=2,
    )

    assert len(result) == len(extraction.knowledge)

    assert [
        record.knowledge
        for record in result
    ] == list(extraction.knowledge)

def test_access_reports_latest_knowledge_state(
    tmp_path,
):
    services = build_document_services()

    source = tmp_path / "document.txt"
    source.write_text(
        "Contenido original.",
        encoding="utf-8",
    )

    artifact = DocumentArtifact.create(
        location=f"local:{source}",
    )

    services.access.add_artifact(artifact)

    document = services.access.create_document(
        name=source.name,
        mime_type="text/plain",
        source=f"local:{source}",
        artifact_id=artifact.id,
    )

    services.document_service.ingest(document)

    assert services.access.has_latest_knowledge(
        document.id,
    ) is False

    source.write_text(
        "Contenido actualizado.",
        encoding="utf-8",
    )

    services.document_service.ingest(document)

    services.document_service.extract_version_knowledge(
        document_id=document.id,
        from_version=1,
        to_version=2,
    )

    assert services.access.has_latest_knowledge(
        document.id,
    ) is True

def test_access_reports_latest_knowledge_count(
    tmp_path,
):
    services = build_document_services()

    source = tmp_path / "document.txt"
    source.write_text(
        "Contenido original.",
        encoding="utf-8",
    )

    artifact = DocumentArtifact.create(
        location=f"local:{source}",
    )

    services.access.add_artifact(artifact)

    document = services.access.create_document(
        name=source.name,
        mime_type="text/plain",
        source=f"local:{source}",
        artifact_id=artifact.id,
    )

    services.document_service.ingest(document)

    assert services.access.knowledge_count(
        document.id,
    ) == 0

    source.write_text(
        "Contenido actualizado.",
        encoding="utf-8",
    )

    services.document_service.ingest(document)

    extraction = services.document_service.extract_version_knowledge(
        document_id=document.id,
        from_version=1,
        to_version=2,
    )

    assert services.access.knowledge_count(
        document.id,
    ) == len(extraction.knowledge)

def test_access_validates_latest_knowledge(
    tmp_path,
):
    services = build_document_services()

    source = tmp_path / "document.txt"
    source.write_text(
        "Contenido original.",
        encoding="utf-8",
    )

    artifact = DocumentArtifact.create(
        location=f"local:{source}",
    )

    services.access.add_artifact(artifact)

    document = services.access.create_document(
        name=source.name,
        mime_type="text/plain",
        source=f"local:{source}",
        artifact_id=artifact.id,
    )

    services.document_service.ingest(document)

    assert services.access.validate_latest_knowledge(
        document.id,
    ) is True

    source.write_text(
        "Contenido actualizado.",
        encoding="utf-8",
    )

    services.document_service.ingest(document)

    services.document_service.extract_version_knowledge(
        document_id=document.id,
        from_version=1,
        to_version=2,
    )

    assert services.access.validate_latest_knowledge(
        document.id,
    ) is True

def test_access_detects_orphaned_knowledge(
    tmp_path,
):
    services = build_document_services()

    source = tmp_path / "document.txt"
    source.write_text(
        "Contenido original.",
        encoding="utf-8",
    )

    artifact = DocumentArtifact.create(
        location=f"local:{source}",
    )

    services.access.add_artifact(artifact)

    document = services.access.create_document(
        name=source.name,
        mime_type="text/plain",
        source=f"local:{source}",
        artifact_id=artifact.id,
    )

    services.document_service.ingest(document)

    source.write_text(
        "Contenido actualizado.",
        encoding="utf-8",
    )

    services.document_service.ingest(document)

    services.document_service.extract_version_knowledge(
        document_id=document.id,
        from_version=1,
        to_version=2,
    )

    assert services.access.has_orphaned_knowledge(
        document.id,
    ) is False

    version = (
        services.content_version_store
        .get_latest_for_document(document.id)
    )

    assert version is not None

    services.content_version_store.remove(
        version.id,
    )

    assert services.access.has_orphaned_knowledge(
        document.id,
    ) is True

def test_access_lists_orphaned_knowledge(
    tmp_path,
):
    services = build_document_services()

    source = tmp_path / "document.txt"
    source.write_text(
        "Contenido original.",
        encoding="utf-8",
    )

    artifact = DocumentArtifact.create(
        location=f"local:{source}",
    )

    services.access.add_artifact(artifact)

    document = services.access.create_document(
        name=source.name,
        mime_type="text/plain",
        source=f"local:{source}",
        artifact_id=artifact.id,
    )

    services.document_service.ingest(document)

    source.write_text(
        "Contenido actualizado.",
        encoding="utf-8",
    )

    services.document_service.ingest(document)

    services.document_service.extract_version_knowledge(
        document_id=document.id,
        from_version=1,
        to_version=2,
    )

    assert services.access.list_orphaned_knowledge(
        document.id,
    ) == []

    version = (
        services.content_version_store
        .get_latest_for_document(document.id)
    )

    assert version is not None

    services.content_version_store.remove(
        version.id,
    )

    orphaned = services.access.list_orphaned_knowledge(
        document.id,
    )

    assert len(orphaned) == 1
    assert orphaned[0].document_id == document.id
    assert orphaned[0].content_version_id == version.id

def test_remove_orphaned_knowledge_delegates_to_service():
    services = build_document_services()

    document = Document.create(
        name="access-orphaned.txt",
        mime_type="text/plain",
        source="memory://access-orphaned.txt",
    )

    services.document_store.add(document)

    assert (
        services.access.remove_orphaned_knowledge(
            document.id
        )
        == 0
    )

def test_remove_knowledge_for_version_through_access(
    tmp_path,
):
    services = build_document_services()

    source = tmp_path / "versioned.txt"
    source.write_text(
        "Contenido inicial.",
        encoding="utf-8",
    )

    artifact = DocumentArtifact.create(
        location=f"local:{source}",
    )

    services.access.add_artifact(artifact)

    document = services.access.create_document(
        name=source.name,
        mime_type="text/plain",
        source=f"local:{source}",
        artifact_id=artifact.id,
    )

    services.document_service.ingest(document)

    source.write_text(
        "Contenido modificado.",
        encoding="utf-8",
    )

    services.document_service.ingest(document)

    services.document_service.extract_version_knowledge(
        document_id=document.id,
        from_version=1,
        to_version=2,
    )

    assert services.access.list_knowledge_for_version(
        document.id,
        2,
    )

    removed = services.access.remove_knowledge_for_version(
        document_id=document.id,
        version=2,
    )

    assert removed == 1

    assert services.access.list_knowledge_for_version(
        document.id,
        2,
    ) == []

def test_refresh_version_knowledge_through_access(
    tmp_path,
):
    services = build_document_services()

    source = tmp_path / "refresh-access.txt"
    source.write_text(
        "Contenido inicial.",
        encoding="utf-8",
    )

    artifact = DocumentArtifact.create(
        location=f"local:{source}",
    )

    services.access.add_artifact(artifact)

    document = services.access.create_document(
        name=source.name,
        mime_type="text/plain",
        source=f"local:{source}",
        artifact_id=artifact.id,
    )

    services.document_service.ingest(document)

    source.write_text(
        "Vigencia: 24 meses.",
        encoding="utf-8",
    )

    services.document_service.ingest(document)

    result = services.access.refresh_version_knowledge(
        document_id=document.id,
        from_version=1,
        to_version=2,
    )

    assert result.knowledge

    records = services.access.list_knowledge_for_version(
        document.id,
        2,
    )

    assert len(records) == len(result.knowledge)

def test_remove_document_through_access_cleans_document_data(
    tmp_path,
):
    services = build_document_services()

    source = tmp_path / "access-delete.txt"
    source.write_text(
        "Contenido inicial.",
        encoding="utf-8",
    )

    artifact = DocumentArtifact.create(
        location=f"local:{source}",
    )

    services.access.add_artifact(artifact)

    document = services.access.create_document(
        name=source.name,
        mime_type="text/plain",
        source=f"local:{source}",
        artifact_id=artifact.id,
    )

    services.document_service.ingest(document)

    source.write_text(
        "Contenido actualizado.",
        encoding="utf-8",
    )

    current_document = services.document_store.get(
        document.id
    )

    assert current_document is not None

    services.document_service.ingest(
        current_document
    )

    removed = services.access.remove_document(
        document.id
    )

    assert removed is not None
    assert removed.id == document.id

    assert services.access.resolve(
        document.id
    ) is None

    assert (
        services.content_version_store.list_for_document(
            document.id
        )
        == []
    )

    assert (
        services.ingestion_record_store.list_for_document(
            document.id
        )
        == []
    )

    assert services.artifact_store.get(
        artifact.id
    ) is artifact

def test_access_can_list_documents_for_user():
    services = build_document_services()

    document = services.access.create_document(
        name="Documento",
        mime_type="text/plain",
        source="document.txt",
        user_id="user-a",
    )

    result = services.access.list_documents_for_user(
        "user-a"
    )

    assert result == [document]


def test_access_can_list_documents_for_organization():
    services = build_document_services()

    document = services.access.create_document(
        name="Documento",
        mime_type="text/plain",
        source="document.txt",
        organization_id="organization-a",
    )

    result = services.access.list_documents_for_organization(
        "organization-a"
    )

    assert result == [document]


def test_access_can_list_documents_for_project():
    services = build_document_services()

    document = services.access.create_document(
        name="Documento",
        mime_type="text/plain",
        source="document.txt",
        project_id="project-a",
    )

    result = services.access.list_documents_for_project(
        "project-a"
    )

    assert result == [document]

def test_access_can_list_documents_for_context():
    services = build_document_services()

    document = services.access.create_document(
        name="Documento",
        mime_type="text/plain",
        source="document.txt",
        user_id="user-a",
        organization_id="organization-a",
        project_id="project-a",
    )

    result = services.access.list_documents_for_context(
        user_id="user-a",
        organization_id="organization-a",
        project_id="project-a",
    )

    assert result == [document]

def test_access_can_get_document():
    services = build_document_services()

    document = services.access.create_document(
        name="document.txt",
        mime_type="text/plain",
        source="document.txt",
    )

    result = services.access.get_document(
        document.id,
    )

    assert result == document


def test_access_returns_none_for_unknown_document():
    services = build_document_services()

    result = services.access.get_document(
        "missing-document",
    )

    assert result is None

def test_access_can_update_document():
    services = build_document_services()

    document = services.access.create_document(
        name="document.txt",
        mime_type="text/plain",
        source="document.txt",
    )

    updated = Document(
        id=document.id,
        name="updated.txt",
        mime_type=document.mime_type,
        source=document.source,
        description=document.description,
        user_id=document.user_id,
        organization_id=document.organization_id,
        project_id=document.project_id,
        artifact_id=document.artifact_id,
        content_id=document.content_id,
        metadata=document.metadata,
        created_at=document.created_at,
        updated_at=document.updated_at,
        ingestion_evidence=document.ingestion_evidence,
    )

    result = services.access.update_document(updated)

    assert result == updated
    assert services.access.get_document(document.id) == updated


def test_access_can_count_documents():
    services = build_document_services()

    assert services.access.count_documents() == 0

    services.access.create_document(
        name="one.txt",
        mime_type="text/plain",
        source="one.txt",
    )

    services.access.create_document(
        name="two.txt",
        mime_type="text/plain",
        source="two.txt",
    )

    assert services.access.count_documents() == 2


def test_access_can_list_documents():
    services = build_document_services()

    first = services.access.create_document(
        name="one.txt",
        mime_type="text/plain",
        source="one.txt",
    )

    second = services.access.create_document(
        name="two.txt",
        mime_type="text/plain",
        source="two.txt",
    )

    result = services.access.list_documents()

    assert result == [first, second]

def test_document_context_types_are_public():
    from documents import (
        DocumentContext,
        DocumentContextAccess,
        DocumentContextResolver,
        DocumentContextSelection,
    )

    assert DocumentContext is not None
    assert DocumentContextAccess is not None
    assert DocumentContextResolver is not None
    assert DocumentContextSelection is not None
