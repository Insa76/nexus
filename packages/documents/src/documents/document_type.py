from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class DocumentType:
    """
    Representa el tipo normalizado de un documento.

    El mime type original puede conservarse por separado en Document.
    Esta abstracción solamente define el tipo que utilizará Documents
    para seleccionar un mecanismo de ingestión.
    """

    mime_type: str

    @property
    def category(self) -> str:
        return self.mime_type.split("/", 1)[0]

    @property
    def subtype(self) -> str:
        return self.mime_type.split("/", 1)[1]

    @classmethod
    def from_mime_type(cls, mime_type: str) -> DocumentType:
        normalized = mime_type.strip().lower()

        if not normalized:
            raise ValueError("mime_type cannot be empty")

        if "/" not in normalized:
            raise ValueError(
                f"Invalid mime type: {mime_type}"
            )

        category, subtype = normalized.split("/", 1)

        if not category or not subtype:
            raise ValueError(
                f"Invalid mime type: {mime_type}"
            )

        return cls(
            mime_type=f"{category}/{subtype}",
        )
