from __future__ import annotations

from documents.ingestion_record import DocumentIngestionRecord


class DocumentIngestionRecordStore:
    def __init__(self) -> None:
        self._records: dict[str, DocumentIngestionRecord] = {}

    def add(
        self,
        record: DocumentIngestionRecord,
    ) -> DocumentIngestionRecord:
        self._records[record.id] = record
        return record

    def get(
        self,
        record_id: str,
    ) -> DocumentIngestionRecord | None:
        return self._records.get(record_id)

    def list(self) -> list[DocumentIngestionRecord]:
        return list(self._records.values())

    def list_for_document(
        self,
        document_id: str,
    ) -> list[DocumentIngestionRecord]:
        return [
            record
            for record in self._records.values()
            if record.document_id == document_id
        ]

    def remove(
        self,
        record_id: str,
    ) -> DocumentIngestionRecord | None:
        return self._records.pop(record_id, None)

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

    def clear(self) -> None:
        self._records.clear()

    def count(self) -> int:
        return len(self._records)
