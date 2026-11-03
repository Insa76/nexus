from __future__ import annotations

import os
import sqlite3
import threading
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path
from typing import Iterator

from rules.models import Rule, RuleStatus


class RuleStore:
    """Repositorio de reglas: SQLite persistente o memoria aislada."""

    def __init__(self, db_path: str | Path | None = None) -> None:
        configured = db_path or os.environ.get("NEXUS_RULES_DB_PATH")
        self._db_path = Path(configured).expanduser() if configured else None
        self._rules: dict[str, Rule] = {}
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
            raise RuntimeError("SQLite is not enabled for this RuleStore.")
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
                CREATE TABLE IF NOT EXISTS nexus_rules (
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
                    f"CREATE INDEX IF NOT EXISTS idx_nexus_rules_{column} "
                    f"ON nexus_rules({column})"
                )

    @staticmethod
    def _from_row(row: sqlite3.Row) -> Rule:
        return Rule(
            id=row["id"],
            name=row["name"],
            description=row["description"],
            status=RuleStatus(row["status"]),
            user_id=row["user_id"],
            organization_id=row["organization_id"],
            project_id=row["project_id"],
            created_at=datetime.fromisoformat(row["created_at"]),
        )

    @staticmethod
    def _values(rule: Rule) -> tuple:
        return (
            rule.id, rule.name, rule.description, rule.status.value,
            rule.user_id, rule.organization_id, rule.project_id,
            rule.created_at.isoformat(),
        )

    def add(self, rule: Rule) -> Rule:
        with self._lock:
            if self._db_path is None:
                self._rules[rule.id] = rule
            else:
                with self._connect() as connection:
                    connection.execute("""
                        INSERT INTO nexus_rules (
                            id, name, description, status, user_id,
                            organization_id, project_id, created_at
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """, self._values(rule))
        return rule

    def get(self, rule_id: str) -> Rule | None:
        with self._lock:
            if self._db_path is None:
                return self._rules.get(rule_id)
            with self._connect() as connection:
                row = connection.execute(
                    "SELECT * FROM nexus_rules WHERE id = ?", (rule_id,)
                ).fetchone()
            return self._from_row(row) if row else None

    def list(self) -> list[Rule]:
        with self._lock:
            if self._db_path is None:
                return list(self._rules.values())
            with self._connect() as connection:
                rows = connection.execute(
                    "SELECT * FROM nexus_rules ORDER BY created_at, id"
                ).fetchall()
            return [self._from_row(row) for row in rows]

    def update(self, rule: Rule) -> Rule:
        with self._lock:
            if self._db_path is None:
                if rule.id not in self._rules:
                    raise KeyError(f"Rule not found: {rule.id}")
                self._rules[rule.id] = rule
            else:
                with self._connect() as connection:
                    cursor = connection.execute("""
                        UPDATE nexus_rules SET name=?, description=?, status=?,
                            user_id=?, organization_id=?, project_id=?, created_at=?
                        WHERE id=?
                    """, (
                        rule.name, rule.description, rule.status.value,
                        rule.user_id, rule.organization_id, rule.project_id,
                        rule.created_at.isoformat(), rule.id,
                    ))
                    if cursor.rowcount == 0:
                        raise KeyError(f"Rule not found: {rule.id}")
        return rule

    def remove(self, rule_id: str) -> Rule | None:
        with self._lock:
            rule = self.get(rule_id)
            if rule is None:
                return None
            if self._db_path is None:
                self._rules.pop(rule_id, None)
            else:
                with self._connect() as connection:
                    connection.execute(
                        "DELETE FROM nexus_rules WHERE id = ?", (rule_id,)
                    )
            return rule

    def clear(self) -> None:
        with self._lock:
            if self._db_path is None:
                self._rules.clear()
            else:
                with self._connect() as connection:
                    connection.execute("DELETE FROM nexus_rules")

    def count(self) -> int:
        with self._lock:
            if self._db_path is None:
                return len(self._rules)
            with self._connect() as connection:
                row = connection.execute(
                    "SELECT COUNT(*) AS total FROM nexus_rules"
                ).fetchone()
            return int(row["total"])
