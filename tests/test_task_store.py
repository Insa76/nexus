from dataclasses import replace

import pytest

from tasks import Task, TaskStore


def test_store_add_and_get_task() -> None:
    store = TaskStore()
    task = Task.create(title="Preparar reunión")

    store.add(task)

    assert store.get(task.id) == task


def test_store_list_tasks() -> None:
    store = TaskStore()

    first = Task.create(title="Primera tarea")
    second = Task.create(title="Segunda tarea")

    store.add(first)
    store.add(second)

    tasks = store.list()

    assert tasks == [first, second]
    assert store.count() == 2


def test_store_update_task() -> None:
    store = TaskStore()

    task = Task.create(title="Preparar reunión")
    store.add(task)

    updated = replace(task, status="completed")
    store.update(updated)

    assert store.get(task.id) == updated
    assert store.get(task.id).status == "completed"


def test_store_update_missing_task_raises() -> None:
    store = TaskStore()

    task = Task.create(title="Tarea inexistente")

    with pytest.raises(KeyError):
        store.update(task)


def test_store_remove_task() -> None:
    store = TaskStore()

    task = Task.create(title="Eliminar tarea")
    store.add(task)

    removed = store.remove(task.id)

    assert removed == task
    assert store.get(task.id) is None
    assert store.count() == 0


def test_store_remove_missing_task_is_safe() -> None:
    store = TaskStore()

    assert store.remove("missing-task") is None


def test_store_clear() -> None:
    store = TaskStore()

    store.add(Task.create(title="Primera"))
    store.add(Task.create(title="Segunda"))

    store.clear()

    assert store.list() == []
    assert store.count() == 0
