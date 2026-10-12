from __future__ import annotations

from documents.document_type import DocumentType


class DocumentTypeResolver:
    """
    Normaliza el tipo de documento a partir de su mime type.

    No inspecciona archivos físicos ni intenta interpretar contenido.
    """

    def resolve(
        self,
        mime_type: str,
    ) -> DocumentType:
        return DocumentType.from_mime_type(
            mime_type
        )
