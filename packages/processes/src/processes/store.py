from __future__ import annotations

import os
import sqlite3
import threading
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path
from typing import Iterator

from processes.models import Process, ProcessStatus


class ProcessStore:
    """Repositorio de procesos: SQLite persistente o memoria aislada."""

    def __init__(self, db_path: str | Path | None = None) -> None:
        configured = db_path or os.environ.get("NEXUS_PROCESSES_DB_PATH")
        self._db_path = Path(configured).expanduser() if configured else None
        self._processes: dict[str, Process] = {}
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
            raise RuntimeError("SQLite is not enabled for this ProcessStore.")
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
                CREATE TABLE IF NOT EXISTS nexus_processes (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    description TEXT,
                    status TEXT NOT NULL,
                    user_id TEXT,
                    organization_id TEXT,
                    project_id TEXT,
                    created_at TEXT NOT NULL
                )
            """)
            for column in ("user_id", "organization_id", "project_id"):
                connection.execute(
                    f"CREATE INDEX IF NOT EXISTS idx_nexus_processes_{column} "
                    f"ON nexus_processes({column})"
                )

    @staticmethod
    def _from_row(row: sqlite3.Row) -> Process:
        return Process(
            id=row["id"],
            name=row["name"],
            description=row["description"],
            status=ProcessStatus(row["status"]),
            user_id=row["user_id"],
            organization_id=row["organization_id"],
            project_id=row["project_id"],
            created_at=datetime.fromisoformat(row["created_at"]),
        )

    @staticmethod
    def _values(process: Process) -> tuple:
        return (
            process.id, process.name, process.description, process.status.value,
            process.user_id, process.organization_id, process.project_id,
            process.created_at.isoformat(),
        )

    def add(self, process: Process) -> Process:
        with self._lock:
            if self._db_path is None:
                self._processes[process.id] = process
            else:
                with self._connect() as connection:
                    connection.execute("""
                        INSERT INTO nexus_processes (
                            id, name, description, status, user_id,
                            organization_id, project_id, created_at
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """, self._values(process))
        return process

    def get(self, process_id: str) -> Process | None:
        with self._lock:
            if self._db_path is None:
                return self._processes.get(process_id)
            with self._connect() as connection:
                row = connection.execute(
                    "SELECT * FROM nexus_processes WHERE id = ?", (process_id,)
                ).fetchone()
            return self._from_row(row) if row else None

    def list(self) -> list[Process]:
        with self._lock:
            if self._db_path is None:
                return list(self._processes.values())
            with self._connect() as connection:
                rows = connection.execute(
                    "SELECT * FROM nexus_processes ORDER BY created_at, id"
                ).fetchall()
            return [self._from_row(row) for row in rows]

    def update(self, process: Process) -> Process:
        with self._lock:
            if self._db_path is None:
                if process.id not in self._processes:
                    raise KeyError(f"Process not found: {process.id}")
                self._processes[process.id] = process
            else:
                with self._connect() as connection:
                    cursor = connection.execute("""
                        UPDATE nexus_processes SET name=?, description=?, status=?,
                            user_id=?, organization_id=?, project_id=?, created_at=?
                        WHERE id=?
                    """, (
                        process.name, process.description, process.status.value,
                        process.user_id, process.organization_id, process.project_id,
                        process.created_at.isoformat(), process.id,
                    ))
                    if cursor.rowcount == 0:
                        raise KeyError(f"Process not found: {process.id}")
        return process

    def remove(self, process_id: str) -> Process | None:
        with self._lock:
            process = self.get(process_id)
            if process is None:
                return None
            if self._db_path is None:
                self._processes.pop(process_id, None)
            else:
                with self._connect() as connection:
                    connection.execute(
                        "DELETE FROM nexus_processes WHERE id = ?", (process_id,)
                    )
            return process

    def clear(self) -> None:
        with self._lock:
            if self._db_path is None:
                self._processes.clear()
            else:
                with self._connect() as connection:
                    connection.execute("DELETE FROM nexus_processes")

    def count(self) -> int:
        with self._lock:
            if self._db_path is None:
                return len(self._processes)
            with self._connect() as connection:
                row = connection.execute(
                    "SELECT COUNT(*) AS total FROM nexus_processes"
                ).fetchone()
            return int(row["total"])
