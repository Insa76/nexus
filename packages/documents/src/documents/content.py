from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from uuid import uuid4


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


@dataclass(frozen=True)
class DocumentContent:
    """
    Contenido procesable de un documento.

    Representa contenido ya disponible para NEXUS, pero no define
    cómo fue obtenido ni cómo se almacena físicamente.
    """

    id: str
    text: str
    content_type: str
    language: str | None = None
    created_at: datetime = field(default_factory=_utc_now)

    @classmethod
    def create(
        cls,
        text: str,
        content_type: str = "text/plain",
        language: str | None = None,
    ) -> DocumentContent:
        return cls(
            id=str(uuid4()),
            text=text,
            content_type=content_type,
            language=language,
            created_at=_utc_now(),
        )
