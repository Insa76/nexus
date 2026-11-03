from __future__ import annotations

import pytest

from context import ContextValidationError, SQLiteContextRepository


def test_context_is_persisted_and_restored(tmp_path):
    database = tmp_path / "nexus-context.sqlite3"
    repository = SQLiteContextRepository(database)

    saved = repository.save({
        "user": {
            "name": "Usuario de prueba",
            "role": "Administrador",
            "preferences": {"language": "es"},
            "responsibilities": ["Producto"],
            "priorities": ["NEXUS"],
        },
        "organization": {
            "name": "Organización de prueba",
            "industry": "Tecnología",
        },
        "project": {
            "name": "Proyecto NEXUS",
            "description": "Contexto persistente.",
        },
    })

    assert saved["user"]["name"] == "Usuario de prueba"
    assert saved["organization"]["name"] == "Organización de prueba"
    assert saved["active_project_id"] == saved["projects"][0]["id"]

    restored = SQLiteContextRepository(database).load_context()

    assert restored.user is not None
    assert restored.user.name == "Usuario de prueba"
    assert restored.user.preferences == {"language": "es"}
    assert restored.organization is not None
    assert restored.organization.name == "Organización de prueba"
    assert len(restored.projects) == 1
    assert restored.projects[0].name == "Proyecto NEXUS"
    assert restored.metadata["active_project_id"] == restored.projects[0].id


def test_context_can_select_only_an_existing_project(tmp_path):
    repository = SQLiteContextRepository(tmp_path / "context.sqlite3")
    repository.save({
        "organization": {"name": "Org"},
        "project": {"name": "Proyecto A"},
    })
    project_id = repository.get_state()["active_project_id"]

    repository.save({"project": {"id": project_id, "name": "Proyecto A actualizado"}})

    context = repository.load_context()
    assert context.projects[0].name == "Proyecto A actualizado"
    assert context.metadata["active_project_id"] == project_id

    with pytest.raises(ContextValidationError):
        repository.save({"active_project_id": "id-ajeno"})


def test_context_can_be_cleared_without_deleting_profile_history(tmp_path):
    repository = SQLiteContextRepository(tmp_path / "context.sqlite3")
    repository.save({
        "user": {"name": "Usuario"},
        "organization": {"name": "Org"},
        "project": {"name": "Proyecto"},
    })

    repository.save({
        "organization": None,
        "project": None,
    })

    state = repository.get_state()
    assert state["user"]["organization_id"] is None
    assert state["organization"] is None
    assert state["active_project_id"] is None
    assert state["projects"][0]["name"] == "Proyecto"
