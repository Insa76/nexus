from __future__ import annotations

import json
import sqlite3
import threading
from datetime import date, datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any

from planner.execution_context import ExecutionContext


class SQLiteExecutionStore:
    """Persist execution checkpoints without replaying side effects."""

    def __init__(self, db_path: str | Path | None = None) -> None:
        if db_path is None:
            db_path = Path.home() / ".nexus" / "executions.sqlite3"

        if str(db_path) == ":memory:":
            self._db_path = ":memory:"
        else:
            path = Path(db_path).expanduser()
            path.parent.mkdir(parents=True, exist_ok=True)
            self._db_path = str(path)

        self._lock = threading.RLock()
        self._connection = sqlite3.connect(
            self._db_path,
            timeout=10.0,
            check_same_thread=False,
        )
        self._connection.row_factory = sqlite3.Row
        self._connection.execute("PRAGMA foreign_keys = ON")
        if self._db_path != ":memory:":
            self._connection.execute("PRAGMA journal_mode = WAL")
        self._initialize_schema()

    def _initialize_schema(self) -> None:
        with self._lock, self._connection:
            self._connection.execute(
                """
                CREATE TABLE IF NOT EXISTS nexus_executions (
                    id TEXT PRIMARY KEY,
                    request_text TEXT NOT NULL,
                    status TEXT NOT NULL,
                    started_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    finished_at TEXT,
                    snapshot_json TEXT NOT NULL,
                    error TEXT
                )
                """
            )
            self._connection.execute(
                "CREATE INDEX IF NOT EXISTS idx_nexus_executions_updated "
                "ON nexus_executions(updated_at DESC)"
            )
            self._connection.execute(
                "CREATE INDEX IF NOT EXISTS idx_nexus_executions_status "
                "ON nexus_executions(status)"
            )

    @staticmethod
    def _json_safe(value: Any) -> Any:
        if value is None or isinstance(value, (str, int, float, bool)):
            return value
        if isinstance(value, (datetime, date)):
            return value.isoformat()
        if isinstance(value, Enum):
            return value.value
        if isinstance(value, bytes):
            return {"type": "bytes", "size": len(value)}
        if isinstance(value, dict):
            return {str(key): SQLiteExecutionStore._json_safe(item) for key, item in value.items()}
        if isinstance(value, (list, tuple, set)):
            return [SQLiteExecutionStore._json_safe(item) for item in value]
        model_dump = getattr(value, "model_dump", None)
        if callable(model_dump):
            try:
                return SQLiteExecutionStore._json_safe(model_dump(mode="json"))
            except Exception:
                try:
                    return SQLiteExecutionStore._json_safe(model_dump())
                except Exception:
                    pass
        if hasattr(value, "size") and hasattr(value, "mode") and value.__class__.__module__.startswith("PIL"):
            width, height = value.size
            return {"type": "image", "width": width, "height": height, "mode": value.mode}
        return {"type": "object", "class": value.__class__.__name__, "repr": repr(value)[:1000]}

    @classmethod
    def _snapshot(cls, context: ExecutionContext) -> str:
        data = {
            "objective": context.objective.model_dump(),
            "plan": context.plan.model_dump(),
            "request_text": context.request_text,
            "actor_id": context.actor_id,
            "actor_type": context.actor_type,
            "variables": context.variables,
            "artifacts": context.artifacts,
            "results": context.results,
            "errors": context.errors,
            "current_step": context.current_step,
            "finished": context.finished,
            "step_evidence": context.step_evidence,
        }
        return json.dumps(cls._json_safe(data), ensure_ascii=False, separators=(",", ":"))

    @staticmethod
    def _now() -> str:
        return datetime.now(timezone.utc).isoformat()

    def begin(self, context: ExecutionContext) -> None:
        now = self._now()
        snapshot = self._snapshot(context)
        with self._lock, self._connection:
            self._connection.execute(
                """
                INSERT INTO nexus_executions (
                    id, request_text, status, started_at, updated_at,
                    finished_at, snapshot_json, error
                ) VALUES (?, ?, 'running', ?, ?, NULL, ?, NULL)
                ON CONFLICT(id) DO UPDATE SET
                    request_text = excluded.request_text,
                    status = 'running',
                    started_at = excluded.started_at,
                    updated_at = excluded.updated_at,
                    finished_at = NULL,
                    snapshot_json = excluded.snapshot_json,
                    error = NULL
                """,
                (context.objective.id, context.request_text, now, now, snapshot),
            )

    def checkpoint(self, context: ExecutionContext) -> None:
        now = self._now()
        snapshot = self._snapshot(context)
        with self._lock, self._connection:
            cursor = self._connection.execute(
                """
                UPDATE nexus_executions
                SET updated_at = ?, snapshot_json = ?
                WHERE id = ? AND status = 'running'
                """,
                (now, snapshot, context.objective.id),
            )
            if cursor.rowcount != 1:
                raise KeyError(f"Execution is not active: {context.objective.id}")

    def finish(self, context: ExecutionContext, *, success: bool, error: str | None = None) -> None:
        now = self._now()
        snapshot = self._snapshot(context)
        status = "completed" if success else "failed"
        with self._lock, self._connection:
            cursor = self._connection.execute(
                """
                UPDATE nexus_executions
                SET status = ?, updated_at = ?, finished_at = ?,
                    snapshot_json = ?, error = ?
                WHERE id = ?
                """,
                (status, now, now, snapshot, error, context.objective.id),
            )
            if cursor.rowcount != 1:
                raise KeyError(f"Execution not found: {context.objective.id}")

    def recover_interrupted(self) -> int:
        """Mark in-flight executions as interrupted; never replay their actions."""
        now = self._now()
        with self._lock, self._connection:
            cursor = self._connection.execute(
                """
                UPDATE nexus_executions
                SET status = 'interrupted',
                    updated_at = ?,
                    finished_at = ?,
                    error = COALESCE(error, 'NEXUS se cerró antes de registrar el resultado. Verificá el efecto antes de volver a intentarlo.')
                WHERE status = 'running'
                """,
                (now, now),
            )
            return int(cursor.rowcount)

    def list(self, limit: int = 50) -> list[dict[str, Any]]:
        bounded_limit = max(1, min(int(limit), 200))
        with self._lock:
            rows = self._connection.execute(
                """
                SELECT id, request_text, status, started_at, updated_at,
                       finished_at, error, snapshot_json
                FROM nexus_executions
                ORDER BY started_at DESC
                LIMIT ?
                """,
                (bounded_limit,),
            ).fetchall()
        result = []
        for row in rows:
            snapshot = json.loads(row["snapshot_json"])
            objective = snapshot.get("objective", {})
            plan = snapshot.get("plan", {})
            result.append({
                "id": row["id"],
                "request_text": row["request_text"],
                "status": row["status"],
                "started_at": row["started_at"],
                "updated_at": row["updated_at"],
                "finished_at": row["finished_at"],
                "error": row["error"],
                "objective": objective,
                "step_count": len(plan.get("steps", [])),
                "completed_steps": sum(
                    1 for step in plan.get("steps", [])
                    if step.get("status") == "completed"
                ),
            })
        return result

    def get(self, execution_id: str) -> dict[str, Any] | None:
        with self._lock:
            row = self._connection.execute(
                "SELECT * FROM nexus_executions WHERE id = ?",
                (execution_id,),
            ).fetchone()
        if row is None:
            return None
        return {
            "id": row["id"],
            "request_text": row["request_text"],
            "status": row["status"],
            "started_at": row["started_at"],
            "updated_at": row["updated_at"],
            "finished_at": row["finished_at"],
            "error": row["error"],
            "snapshot": json.loads(row["snapshot_json"]),
        }

    def count(self) -> int:
        with self._lock:
            row = self._connection.execute(
                "SELECT COUNT(*) AS total FROM nexus_executions"
            ).fetchone()
        return int(row["total"])

    def close(self) -> None:
        with self._lock:
            self._connection.close()
