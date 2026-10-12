from __future__ import annotations

from documents.document_type import DocumentType
from documents.type_validation import DocumentTypeValidation


class DocumentTypeValidator:
    def validate(
        self,
        declared_type: str | DocumentType,
        detected_type: DocumentType,
    ) -> DocumentTypeValidation:
        resolved_declared_type = (
            declared_type
            if isinstance(
                declared_type,
                DocumentType,
            )
            else DocumentType.from_mime_type(
                declared_type
            )
        )

        return DocumentTypeValidation(
            declared_type=resolved_declared_type,
            detected_type=detected_type,
        )
