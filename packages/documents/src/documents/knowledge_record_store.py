from __future__ import annotations

from documents.knowledge_record import DocumentKnowledgeRecord



class DocumentKnowledgeRecordStore:
    def __init__(self) -> None:
        self._records: dict[str, DocumentKnowledgeRecord] = {}

    def add(
        self,
        record: DocumentKnowledgeRecord,
    ) -> DocumentKnowledgeRecord:
        self._records[record.id] = record
        return record

    def get(
        self,
        record_id: str,
    ) -> DocumentKnowledgeRecord | None:
        return self._records.get(record_id)

    def list(self) -> list[DocumentKnowledgeRecord]:
        return list(self._records.values())

    def list_for_document(
        self,
        document_id: str,
    ) -> list[DocumentKnowledgeRecord]:
        return [
            record
            for record in self._records.values()
            if record.document_id == document_id
        ]

    def list_for_content_version(
        self,
        content_version_id: str,
    ) -> list[DocumentKnowledgeRecord]:
        return [
            record
            for record in self._records.values()
            if record.content_version_id == content_version_id
        ]

    def find(
        self,
        *,
        document_id: str,
        content_version_id: str,
        knowledge: DocumentKnowledge,
    ) -> DocumentKnowledgeRecord | None:
        for record in self._records.values():
            if (
                record.document_id == document_id
                and record.content_version_id == content_version_id
                and record.knowledge == knowledge
            ):
                return record

        return None

    def remove_for_content_version(
        self,
        content_version_id: str,
    ) -> int:
        records = [
            record
            for record in self._records.values()
            if record.content_version_id == content_version_id
        ]

        for record in records:
            self._records.pop(record.id, None)

        return len(records)

    def remove_for_document(
        self,
        document_id: str,
    ) -> int:
        records = [
            record
            for record in self._records.values()
            if record.document_id == document_id
        ]

        for record in records:
            self._records.pop(record.id, None)

        return len(records)

    def remove(
        self,
        record_id: str,
    ) -> DocumentKnowledgeRecord | None:
        return self._records.pop(record_id, None)

    def clear(self) -> None:
        self._records.clear()

    def count(self) -> int:
        return len(self._records)
