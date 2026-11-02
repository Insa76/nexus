
from __future__ import annotations

import sqlite3
import threading
from datetime import datetime
from pathlib import Path

from tasks.reminders import Reminder, ReminderStatus


class ReminderStore:
    """SQLite-backed store for assistant reminders."""

    def __init__(
        self,
        db_path: str | Path | None = None,
    ) -> None:
        self._lock = threading.RLock()

        if db_path is None or str(db_path) == ":memory:":
            resolved_path = ":memory:"
        else:
            path = Path(db_path).expanduser()
            path.parent.mkdir(parents=True, exist_ok=True)
            resolved_path = str(path)

        self._connection = sqlite3.connect(
            resolved_path,
            timeout=10.0,
            check_same_thread=False,
        )
        self._connection.row_factory = sqlite3.Row
        self._connection.execute("PRAGMA foreign_keys = ON")

        if resolved_path != ":memory:":
            self._connection.execute("PRAGMA journal_mode = WAL")

        self._initialize_schema()

    def _initialize_schema(self) -> None:
        with self._lock, self._connection:
            self._connection.execute(
                """
                CREATE TABLE IF NOT EXISTS reminders (
                    id TEXT PRIMARY KEY,
                    message TEXT NOT NULL,
                    trigger_at TEXT NOT NULL,
                    status TEXT NOT NULL,
                    task_id TEXT,
                    user_id TEXT,
                    organization_id TEXT,
                    project_id TEXT,
                    created_at TEXT NOT NULL
                )
                """
            )

    @staticmethod
    def _to_reminder(row: sqlite3.Row | None) -> Reminder | None:
        if row is None:
            return None

        return Reminder(
            id=row["id"],
            message=row["message"],
            trigger_at=datetime.fromisoformat(row["trigger_at"]),
            status=ReminderStatus(row["status"]),
            task_id=row["task_id"],
            user_id=row["user_id"],
            organization_id=row["organization_id"],
            project_id=row["project_id"],
            created_at=datetime.fromisoformat(row["created_at"]),
        )

    def _save(self, reminder: Reminder) -> None:
        self._connection.execute(
            """
            INSERT INTO reminders (
                id, message, trigger_at, status, task_id,
                user_id, organization_id, project_id, created_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(id) DO UPDATE SET
                message = excluded.message,
                trigger_at = excluded.trigger_at,
                status = excluded.status,
                task_id = excluded.task_id,
                user_id = excluded.user_id,
                organization_id = excluded.organization_id,
                project_id = excluded.project_id,
                created_at = excluded.created_at
            """,
            (
                reminder.id,
                reminder.message,
                reminder.trigger_at.isoformat(),
                reminder.status.value,
                reminder.task_id,
                reminder.user_id,
                reminder.organization_id,
                reminder.project_id,
                reminder.created_at.isoformat(),
            ),
        )

    def add(self, reminder: Reminder) -> Reminder:
        with self._lock, self._connection:
            self._save(reminder)
        return reminder

    def get(self, reminder_id: str) -> Reminder | None:
        with self._lock:
            row = self._connection.execute(
                "SELECT * FROM reminders WHERE id = ?",
                (reminder_id,),
            ).fetchone()

        return self._to_reminder(row)

    def list(self) -> list[Reminder]:
        with self._lock:
            rows = self._connection.execute(
                "SELECT * FROM reminders ORDER BY rowid"
            ).fetchall()

        return [
            reminder
            for row in rows
            if (reminder := self._to_reminder(row)) is not None
        ]

    def update(self, reminder: Reminder) -> Reminder:
        with self._lock, self._connection:
            exists = self._connection.execute(
                "SELECT 1 FROM reminders WHERE id = ?",
                (reminder.id,),
            ).fetchone()

            if exists is None:
                raise KeyError(f"Reminder not found: {reminder.id}")

            self._save(reminder)

        return reminder

    def remove(self, reminder_id: str) -> Reminder | None:
        with self._lock, self._connection:
            row = self._connection.execute(
                "SELECT * FROM reminders WHERE id = ?",
                (reminder_id,),
            ).fetchone()

            reminder = self._to_reminder(row)

            if reminder is not None:
                self._connection.execute(
                    "DELETE FROM reminders WHERE id = ?",
                    (reminder_id,),
                )

        return reminder

    def clear(self) -> None:
        with self._lock, self._connection:
            self._connection.execute("DELETE FROM reminders")

    def count(self) -> int:
        with self._lock:
            row = self._connection.execute(
                "SELECT COUNT(*) AS total FROM reminders"
            ).fetchone()

        return int(row["total"])

    def close(self) -> None:
        """Close the SQLite connection."""
        with self._lock:
            self._connection.close()
