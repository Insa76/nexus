from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class DocumentMetadata:
    """
    Metadata descriptiva y semántica de un documento.

    No representa el artefacto físico ni su almacenamiento.
    """

    filename: str | None = None
    title: str | None = None
    author: str | None = None
    language: str | None = None
    document_type: str | None = None
    tags: tuple[str, ...] = ()
    extra: dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> dict[str, object]:
        return {
            "filename": self.filename,
            "title": self.title,
            "author": self.author,
            "language": self.language,
            "document_type": self.document_type,
            "tags": self.tags,
            "extra": dict(self.extra),
        }

    @classmethod
    def from_dict(
        cls,
        metadata: dict[str, object] | None = None,
    ) -> DocumentMetadata:
        data = dict(metadata or {})

        raw_tags = data.pop("tags", ())
        tags = tuple(str(tag) for tag in raw_tags) if raw_tags else ()

        known_fields = {
            "filename",
            "title",
            "author",
            "language",
            "document_type",
        }

        values = {
            key: data.pop(key, None)
            for key in known_fields
        }

        extra = {
            str(key): str(value)
            for key, value in data.items()
        }

        return cls(
            filename=values["filename"],
            title=values["title"],
            author=values["author"],
            language=values["language"],
            document_type=values["document_type"],
            tags=tags,
            extra=extra,
        )
