from __future__ import annotations

from pathlib import Path

from documents.artifacts import DocumentArtifact
from documents.sources import DocumentSource


class LocalArtifactReader:
    def __init__(
        self,
        encoding: str = "utf-8",
    ) -> None:
        self._encoding = encoding

    def read(
        self,
        artifact: DocumentArtifact,
    ) -> str:
        source = DocumentSource.from_location(
            artifact.location
        )

        if source.scheme != "local":
            raise ValueError(
                "LocalArtifactReader cannot read source scheme: "
                f"{source.scheme}"
            )

        path = Path(
            source.location
        )

        return path.read_text(
            encoding=self._encoding
        )
