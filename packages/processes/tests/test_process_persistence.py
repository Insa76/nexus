from dataclasses import replace

from processes import Process, ProcessStatus, ProcessStore


def test_process_store_persists_and_reopens(tmp_path):
    db_path = tmp_path / "processes.sqlite3"
    original = Process.create(
        "Proceso persistente",
        description="Conserva su estado",
        user_id="user-1",
        organization_id="org-1",
        project_id="project-1",
    )
    first = ProcessStore(db_path=db_path)
    first.add(original)

    reopened = ProcessStore(db_path=db_path)
    assert reopened.get(original.id) == original
    assert reopened.list() == [original]
    assert reopened.count() == 1

    updated = replace(original, status=ProcessStatus.IN_PROGRESS)
    reopened.update(updated)
    assert ProcessStore(db_path=db_path).get(original.id) == updated

    assert reopened.remove(original.id) == updated
    assert ProcessStore(db_path=db_path).count() == 0


def test_process_store_keeps_memory_mode_without_db_path():
    store = ProcessStore()
    process = Process.create("Proceso temporal")
    store.add(process)
    assert store.get(process.id) == process
