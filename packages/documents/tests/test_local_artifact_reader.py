from pathlib import Path

import pytest

from documents import DocumentArtifact, LocalArtifactReader


def test_read_local_artifact(tmp_path: Path):
    file_path = tmp_path / "document.txt"
    file_path.write_text(
        "Contenido local.",
        encoding="utf-8",
    )

    artifact = DocumentArtifact.create(
        location=f"local:{file_path}",
    )

    reader = LocalArtifactReader()

    assert reader.read(artifact) == "Contenido local."


def test_read_direct_path(tmp_path: Path):
    file_path = tmp_path / "document.txt"
    file_path.write_text(
        "Contenido directo.",
        encoding="utf-8",
    )

    artifact = DocumentArtifact.create(
        location=str(file_path),
    )

    reader = LocalArtifactReader()

    assert reader.read(artifact) == "Contenido directo."


def test_read_utf8_content(tmp_path: Path):
    file_path = tmp_path / "document.txt"
    file_path.write_text(
        "Información de administración: acción, operación y gestión.",
        encoding="utf-8",
    )

    artifact = DocumentArtifact.create(
        location=f"local:{file_path}",
    )

    reader = LocalArtifactReader()

    assert reader.read(artifact) == (
        "Información de administración: acción, operación y gestión."
    )


def test_read_missing_file_raises(tmp_path: Path):
    file_path = tmp_path / "missing.txt"

    artifact = DocumentArtifact.create(
        location=f"local:{file_path}",
    )

    reader = LocalArtifactReader()

    with pytest.raises(FileNotFoundError):
        reader.read(artifact)


def test_custom_encoding(tmp_path: Path):
    file_path = tmp_path / "document.txt"
    file_path.write_text(
        "Contenido.",
        encoding="utf-8",
    )

    artifact = DocumentArtifact.create(
        location=f"local:{file_path}",
    )

    reader = LocalArtifactReader(encoding="utf-8")

    assert reader.read(artifact) == "Contenido."

def test_local_reader_rejects_non_local_source():
    artifact = DocumentArtifact.create(
        location="remote:test.txt",
    )

    reader = LocalArtifactReader()

    with pytest.raises(ValueError):
        reader.read(artifact)
