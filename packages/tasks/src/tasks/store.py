from __future__ import annotations

import os
import sqlite3
import threading
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path
from typing import Iterator

from tasks.models import Task, TaskStatus


class TaskStore:
    """Repositorio de tareas: SQLite persistente o memoria aislada para tests."""

    def __init__(self, db_path: str | Path | None = None) -> None:
        configured = db_path or os.environ.get("NEXUS_TASKS_DB_PATH")
        self._db_path = Path(configured).expanduser() if configured else None
        self._tasks: dict[str, Task] = {}
        self._lock = threading.RLock()
        if self._db_path is not None:
            self._db_path.parent.mkdir(parents=True, exist_ok=True)
            self._initialize()

    @property
    def db_path(self) -> Path | None:
        return self._db_path

    @contextmanager
    def _connect(self) -> Iterator[sqlite3.Connection]:
        if self._db_path is None:
            raise RuntimeError("SQLite is not enabled for this TaskStore.")
        connection = sqlite3.connect(str(self._db_path), timeout=10)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA busy_timeout = 10000")
        try:
            yield connection
            connection.commit()
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()

    def _initialize(self) -> None:
        with self._connect() as connection:
            connection.execute("""
                CREATE TABLE IF NOT EXISTS nexus_tasks (
                    id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    description TEXT,
                    status TEXT NOT NULL,
                    priority TEXT NOT NULL,
                    user_id TEXT,
                    organization_id TEXT,
                    project_id TEXT,
                    due_at TEXT,
                    created_at TEXT NOT NULL
                )
            """)
            for column in ("user_id", "organization_id", "project_id"):
                connection.execute(
                    f"CREATE INDEX IF NOT EXISTS idx_nexus_tasks_{column} "
                    f"ON nexus_tasks({column})"
                )

    @staticmethod
    def _from_row(row: sqlite3.Row) -> Task:
        return Task(
            id=row["id"], title=row["title"], description=row["description"],
            status=TaskStatus(row["status"]), priority=row["priority"],
            user_id=row["user_id"], organization_id=row["organization_id"],
            project_id=row["project_id"],
            due_at=datetime.fromisoformat(row["due_at"]) if row["due_at"] else None,
            created_at=datetime.fromisoformat(row["created_at"]),
        )

    @staticmethod
    def _values(task: Task) -> tuple:
        return (
            task.id, task.title, task.description, task.status.value,
            task.priority, task.user_id, task.organization_id, task.project_id,
            task.due_at.isoformat() if task.due_at else None,
            task.created_at.isoformat(),
        )

    def add(self, task: Task) -> Task:
        with self._lock:
            if self._db_path is None:
                self._tasks[task.id] = task
            else:
                with self._connect() as connection:
                    connection.execute("""
                        INSERT INTO nexus_tasks (
                            id, title, description, status, priority, user_id,
                            organization_id, project_id, due_at, created_at
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, self._values(task))
        return task

    def get(self, task_id: str) -> Task | None:
        with self._lock:
            if self._db_path is None:
                return self._tasks.get(task_id)
            with self._connect() as connection:
                row = connection.execute(
                    "SELECT * FROM nexus_tasks WHERE id = ?", (task_id,)
                ).fetchone()
            return self._from_row(row) if row else None

    def list(self) -> list[Task]:
        with self._lock:
            if self._db_path is None:
                return list(self._tasks.values())
            with self._connect() as connection:
                rows = connection.execute(
                    "SELECT * FROM nexus_tasks ORDER BY created_at, id"
                ).fetchall()
            return [self._from_row(row) for row in rows]

    def update(self, task: Task) -> Task:
        with self._lock:
            if self._db_path is None:
                if task.id not in self._tasks:
                    raise KeyError(f"Task not found: {task.id}")
                self._tasks[task.id] = task
            else:
                with self._connect() as connection:
                    cursor = connection.execute("""
                        UPDATE nexus_tasks SET title=?, description=?, status=?,
                            priority=?, user_id=?, organization_id=?, project_id=?,
                            due_at=?, created_at=? WHERE id=?
                    """, (
                        task.title, task.description, task.status.value,
                        task.priority, task.user_id, task.organization_id,
                        task.project_id,
                        task.due_at.isoformat() if task.due_at else None,
                        task.created_at.isoformat(), task.id,
                    ))
                    if cursor.rowcount == 0:
                        raise KeyError(f"Task not found: {task.id}")
        return task

    def remove(self, task_id: str) -> Task | None:
        with self._lock:
            task = self.get(task_id)
            if task is None:
                return None
            if self._db_path is None:
                self._tasks.pop(task_id, None)
            else:
                with self._connect() as connection:
                    connection.execute(
                        "DELETE FROM nexus_tasks WHERE id = ?", (task_id,)
                    )
            return task

    def clear(self) -> None:
        with self._lock:
            if self._db_path is None:
                self._tasks.clear()
            else:
                with self._connect() as connection:
                    connection.execute("DELETE FROM nexus_tasks")

    def count(self) -> int:
        with self._lock:
            if self._db_path is None:
                return len(self._tasks)
            with self._connect() as connection:
                row = connection.execute(
                    "SELECT COUNT(*) AS total FROM nexus_tasks"
                ).fetchone()
            return int(row["total"])
