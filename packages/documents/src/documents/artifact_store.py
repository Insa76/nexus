from __future__ import annotations

from documents.artifacts import DocumentArtifact


class ArtifactStore:
    def __init__(self) -> None:
        self._artifacts: dict[str, DocumentArtifact] = {}

    def add(self, artifact: DocumentArtifact) -> DocumentArtifact:
        self._artifacts[artifact.id] = artifact
        return artifact

    def get(self, artifact_id: str) -> DocumentArtifact | None:
        return self._artifacts.get(artifact_id)

    def list(self) -> list[DocumentArtifact]:
        return list(self._artifacts.values())

    def update(self, artifact: DocumentArtifact) -> DocumentArtifact:
        if artifact.id not in self._artifacts:
            raise KeyError(f"Artifact not found: {artifact.id}")

        self._artifacts[artifact.id] = artifact
        return artifact

    def remove(self, artifact_id: str) -> DocumentArtifact | None:
        return self._artifacts.pop(artifact_id, None)

    def clear(self) -> None:
        self._artifacts.clear()

    def count(self) -> int:
        return len(self._artifacts)
