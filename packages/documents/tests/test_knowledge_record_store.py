from documents import (
    DocumentChange,
    DocumentKnowledge,
    DocumentKnowledgeRecord,
    DocumentKnowledgeRecordStore,
    DocumentSemanticChange,
    DocumentChangeType,

)


def build_record(
    document_id: str = "doc-1",
    content_version_id: str = "version-1",
) -> DocumentKnowledgeRecord:
    change = DocumentChange.modified(
        "Vigencia: 12 meses.",
        "Vigencia: 24 meses.",
        before_line=1,
        after_line=1,
    )

    semantic_change = DocumentSemanticChange(
        source_change=change,
        meaning="Se modificó la vigencia.",
        topics=("vigencia",),
        confidence=0.9,
    )

    knowledge = DocumentKnowledge(
        source_change=semantic_change,
        statement="La vigencia cambió.",
        topic="vigencia",
        confidence=0.9,
    )

    return DocumentKnowledgeRecord.create(
        document_id=document_id,
        content_version_id=content_version_id,
        knowledge=knowledge,
    )


def test_add_and_get():
    store = DocumentKnowledgeRecordStore()
    record = build_record()

    store.add(record)

    assert store.get(record.id) == record


def test_get_returns_none_when_missing():
    store = DocumentKnowledgeRecordStore()

    assert store.get("missing") is None


def test_list_returns_all_records():
    store = DocumentKnowledgeRecordStore()

    first = build_record(
        document_id="doc-1",
        content_version_id="version-1",
    )
    second = build_record(
        document_id="doc-2",
        content_version_id="version-2",
    )

    store.add(first)
    store.add(second)

    assert store.list() == [first, second]


def test_list_for_document():
    store = DocumentKnowledgeRecordStore()

    first = build_record(document_id="doc-1")
    second = build_record(document_id="doc-2")

    store.add(first)
    store.add(second)

    assert store.list_for_document("doc-1") == [first]
    assert store.list_for_document("doc-2") == [second]


def test_list_for_content_version():
    store = DocumentKnowledgeRecordStore()

    first = build_record(
        document_id="doc-1",
        content_version_id="version-1",
    )
    second = build_record(
        document_id="doc-1",
        content_version_id="version-2",
    )

    store.add(first)
    store.add(second)

    assert store.list_for_content_version("version-1") == [first]
    assert store.list_for_content_version("version-2") == [second]


def test_remove():
    store = DocumentKnowledgeRecordStore()
    record = build_record()

    store.add(record)

    removed = store.remove(record.id)

    assert removed == record
    assert store.get(record.id) is None


def test_clear():
    store = DocumentKnowledgeRecordStore()

    store.add(build_record())
    store.add(build_record(document_id="doc-2"))

    store.clear()

    assert store.list() == []
    assert store.count() == 0


def test_count():
    store = DocumentKnowledgeRecordStore()

    assert store.count() == 0

    store.add(build_record())
    assert store.count() == 1

    store.add(build_record(document_id="doc-2"))
    assert store.count() == 2

def test_find_returns_matching_knowledge_record():
    store = DocumentKnowledgeRecordStore()

    knowledge = DocumentKnowledge(
        source_change=DocumentSemanticChange(
            source_change=DocumentChange(
                change_type=DocumentChangeType.MODIFIED,
                before="A",
                after="B",
            ),
            meaning="Cambio",
        ),
        statement="Se modificó contenido.",
    )

    record = DocumentKnowledgeRecord.create(
        document_id="document-1",
        content_version_id="version-1",
        knowledge=knowledge,
    )

    store.add(record)

    result = store.find(
        document_id="document-1",
        content_version_id="version-1",
        knowledge=knowledge,
    )

    assert result == record

def test_find_returns_none_for_non_matching_knowledge_record():
    store = DocumentKnowledgeRecordStore()

    knowledge = DocumentKnowledge(
        source_change=DocumentSemanticChange(
            source_change=DocumentChange(
                change_type=DocumentChangeType.MODIFIED,
                before="A",
                after="B",
            ),
            meaning="Cambio",
        ),
        statement="Se modificó contenido.",
    )

    record = DocumentKnowledgeRecord.create(
        document_id="document-1",
        content_version_id="version-1",
        knowledge=knowledge,
    )

    store.add(record)

    result = store.find(
        document_id="document-1",
        content_version_id="version-1",
        knowledge=DocumentKnowledge(
            source_change=DocumentSemanticChange(
                source_change=DocumentChange(
                    change_type=DocumentChangeType.MODIFIED,
                    before="X",
                    after="Y",
                ),
                meaning="Otro cambio",
            ),
            statement="Otro conocimiento.",
        ),
    )

    assert result is None

def test_remove_for_content_version_removes_only_matching_records():
    store = DocumentKnowledgeRecordStore()

    record_v1 = DocumentKnowledgeRecord.create(
        document_id="document-1",
        content_version_id="version-1",
        knowledge=DocumentKnowledge(
            source_change=DocumentSemanticChange(
                source_change=DocumentChange(
                    change_type=DocumentChangeType.MODIFIED,
                    before="A",
                    after="B",
                ),
                meaning="Se modificó contenido existente del documento.",
            ),
            statement="Se modificó contenido existente del documento.",
        ),
    )

    record_v2 = DocumentKnowledgeRecord.create(
        document_id="document-1",
        content_version_id="version-2",
        knowledge=DocumentKnowledge(
            source_change=DocumentSemanticChange(
                source_change=DocumentChange(
                    change_type=DocumentChangeType.MODIFIED,
                    before="B",
                    after="C",
                ),
                meaning="Se modificó contenido existente del documento.",
            ),
            statement="Se modificó contenido existente del documento.",
        ),
    )

    store.add(record_v1)
    store.add(record_v2)

    removed = store.remove_for_content_version(
        "version-1"
    )

    assert removed == 1
    assert store.get(record_v1.id) is None
    assert store.get(record_v2.id) == record_v2
