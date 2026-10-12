from __future__ import annotations

from documents.content import DocumentContent


class ContentStore:
    def __init__(self) -> None:
        self._contents: dict[str, DocumentContent] = {}

    def add(self, content: DocumentContent) -> DocumentContent:
        self._contents[content.id] = content
        return content

    def get(self, content_id: str) -> DocumentContent | None:
        return self._contents.get(content_id)

    def list(self) -> list[DocumentContent]:
        return list(self._contents.values())

    def update(self, content: DocumentContent) -> DocumentContent:
        if content.id not in self._contents:
            raise KeyError(f"Content not found: {content.id}")

        self._contents[content.id] = content
        return content

    def remove(self, content_id: str) -> DocumentContent | None:
        return self._contents.pop(content_id, None)

    def clear(self) -> None:
        self._contents.clear()

    def count(self) -> int:
        return len(self._contents)
