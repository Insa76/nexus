from pathlib import Path

from memory.semantic_memory import SemanticMemory


def test_semantic_memory_persists_facts_after_reopen(tmp_path: Path) -> None:
    db_path = tmp_path / "semantic.db"
    first = SemanticMemory(db_path=db_path)
    first.learn("User", "Favorite color", "blue", metadata={"source": "test"})
    first.close()

    second = SemanticMemory(db_path=db_path)
    fact = second.get("user", "favorite color")
    assert fact is not None
    assert fact.value == "blue"
    assert fact.metadata == {"source": "test"}
    second.close()


def test_semantic_memory_updates_and_forgets_persistently(tmp_path: Path) -> None:
    db_path = tmp_path / "semantic.db"
    memory = SemanticMemory(db_path=db_path)
    memory.learn("user", "favorite color", "blue")
    memory.learn("user", "favorite color", "green")
    assert memory.get_value("user", "favorite color") == "green"
    assert memory.forget("user", "favorite color") is True
    assert memory.get_value("user", "favorite color") is None
    assert memory.forget("user", "favorite color") is False
    memory.close()


def test_semantic_memory_clear_removes_persisted_facts(tmp_path: Path) -> None:
    db_path = tmp_path / "semantic.db"
    memory = SemanticMemory(db_path=db_path)
    memory.learn("user", "project", "NEXUS")
    memory.clear()
    assert memory.count() == 0
    memory.close()

    reopened = SemanticMemory(db_path=db_path)
    assert reopened.count() == 0
    reopened.close()
