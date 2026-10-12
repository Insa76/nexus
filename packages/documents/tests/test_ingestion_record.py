from documents import (
    DocumentIngestionRecord,
    DocumentIngestionRecordStore,
)


def test_ingestion_record_creation():
    record = DocumentIngestionRecord.create(
        document_id="document-1",
        artifact_id="artifact-1",
        content_id="content-1",
        declared_type="text/plain",
        detected_type="text/plain",
        detection_strategy="ExtensionTypeDetectionStrategy",
    )

    assert record.id
    assert record.document_id == "document-1"
    assert record.artifact_id == "artifact-1"
    assert record.content_id == "content-1"

    assert record.declared_type.mime_type == "text/plain"
    assert record.detected_type is not None
    assert record.detected_type.mime_type == "text/plain"

    assert (
        record.detection_strategy
        == "ExtensionTypeDetectionStrategy"
    )

    assert record.type_matches is True
    assert record.type_mismatch is False
    assert record.created_at is not None


def test_ingestion_record_detects_mismatch():
    record = DocumentIngestionRecord.create(
        document_id="document-1",
        artifact_id="artifact-1",
        content_id="content-1",
        declared_type="text/plain",
        detected_type="application/json",
        detection_strategy="ExtensionTypeDetectionStrategy",
    )

    assert record.type_matches is False
    assert record.type_mismatch is True


def test_ingestion_record_supports_legacy_ingestion_without_detection():
    record = DocumentIngestionRecord.create(
        document_id="document-1",
        artifact_id="artifact-1",
        content_id="content-1",
        declared_type="text/plain",
    )

    assert record.declared_type.mime_type == "text/plain"
    assert record.detected_type is None
    assert record.detection_strategy is None
    assert record.type_matches is None
    assert record.type_mismatch is None


def test_ingestion_record_is_immutable():
    record = DocumentIngestionRecord.create(
        document_id="document-1",
        artifact_id="artifact-1",
        content_id="content-1",
        declared_type="text/plain",
    )

    try:
        record.document_id = "other"
    except Exception:
        pass
    else:
        raise AssertionError("DocumentIngestionRecord must be immutable")


def test_ingestion_record_store_crud():
    store = DocumentIngestionRecordStore()

    record = DocumentIngestionRecord.create(
        document_id="document-1",
        artifact_id="artifact-1",
        content_id="content-1",
        declared_type="text/plain",
    )

    assert store.count() == 0

    added = store.add(record)

    assert added is record
    assert store.count() == 1
    assert store.get(record.id) is record
    assert store.list() == [record]

    removed = store.remove(record.id)

    assert removed is record
    assert store.get(record.id) is None
    assert store.count() == 0


def test_ingestion_record_store_lists_records_for_document():
    store = DocumentIngestionRecordStore()

    first = DocumentIngestionRecord.create(
        document_id="document-1",
        artifact_id="artifact-1",
        content_id="content-1",
        declared_type="text/plain",
    )

    second = DocumentIngestionRecord.create(
        document_id="document-1",
        artifact_id="artifact-2",
        content_id="content-2",
        declared_type="text/plain",
    )

    other = DocumentIngestionRecord.create(
        document_id="document-2",
        artifact_id="artifact-3",
        content_id="content-3",
        declared_type="text/plain",
    )

    store.add(first)
    store.add(second)
    store.add(other)

    records = store.list_for_document("document-1")

    assert records == [first, second]


def test_ingestion_record_store_clear():
    store = DocumentIngestionRecordStore()

    record = DocumentIngestionRecord.create(
        document_id="document-1",
        artifact_id="artifact-1",
        content_id="content-1",
        declared_type="text/plain",
    )

    store.add(record)

    assert store.count() == 1

    store.clear()

    assert store.count() == 0
    assert store.list() == []

def test_remove_for_document_removes_only_matching_records():
    store = DocumentIngestionRecordStore()

    first = DocumentIngestionRecord.create(
        document_id="doc-1",
        artifact_id="artifact-1",
        content_id="content-1",
        declared_type="text/plain",
    )

    second = DocumentIngestionRecord.create(
        document_id="doc-2",
        artifact_id="artifact-2",
        content_id="content-2",
        declared_type="text/plain",
    )

    store.add(first)
    store.add(second)

    removed = store.remove_for_document(
        "doc-1"
    )

    assert removed == 1
    assert store.get(first.id) is None
    assert store.get(second.id) == second
