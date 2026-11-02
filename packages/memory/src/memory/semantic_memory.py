
from __future__ import annotations

import json
import sqlite3
import threading
from dataclasses import dataclass, field
from datetime import datetime, timezone
from functools import wraps
from pathlib import Path
from typing import Any


def _thread_safe(method):
    """Serializa el acceso a la conexión SQLite compartida."""

    @wraps(method)
    def wrapper(self, *args, **kwargs):
        with self._lock:
            return method(self, *args, **kwargs)

    return wrapper


@dataclass
class SemanticFact:
    """Representa una unidad de conocimiento semántico reutilizable."""

    subject: str
    predicate: str
    value: Any
    confidence: float = 1.0
    source: str = "system"
    created_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    updated_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    metadata: dict[str, Any] = field(default_factory=dict)


class SemanticMemory:
    """Memoria semántica con persistencia SQLite opcional.

    Si db_path es None, usa una base SQLite en memoria.
    Para persistencia entre reinicios, se debe proporcionar una ruta.
    """

    def __init__(self, db_path: str | Path | None = None) -> None:
        self._lock = threading.RLock()
        self._fact_cache: dict[tuple[str, str], SemanticFact] = {}

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

    @_thread_safe
    def _initialize_schema(self) -> None:
        with self._connection:
            self._connection.execute(
                """
                CREATE TABLE IF NOT EXISTS semantic_facts (
                    subject TEXT NOT NULL,
                    predicate TEXT NOT NULL,
                    value_json TEXT NOT NULL,
                    confidence REAL NOT NULL,
                    source TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    metadata_json TEXT NOT NULL,
                    PRIMARY KEY (subject, predicate)
                )
                """
            )

    @staticmethod
    def _normalize(value: str) -> str:
        if not isinstance(value, str):
            raise TypeError("SemanticMemory values must be strings.")
        return " ".join(value.strip().lower().split())

    @staticmethod
    def _normalize_confidence(confidence: float) -> float:
        try:
            confidence = float(confidence)
        except (TypeError, ValueError) as exc:
            raise ValueError(
                "SemanticFact confidence must be numeric."
            ) from exc

        return max(0.0, min(1.0, confidence))

    def _to_fact(
        self,
        row: sqlite3.Row | None,
    ) -> SemanticFact | None:
        """Convierte una fila SQLite y conserva la identidad del objeto."""

        if row is None:
            return None

        key = (row["subject"], row["predicate"])

        value = json.loads(row["value_json"])
        confidence = float(row["confidence"])
        source = row["source"]
        created_at = datetime.fromisoformat(row["created_at"])
        updated_at = datetime.fromisoformat(row["updated_at"])
        metadata = json.loads(row["metadata_json"])

        fact = self._fact_cache.get(key)

        if fact is None:
            fact = SemanticFact(
                subject=row["subject"],
                predicate=row["predicate"],
                value=value,
                confidence=confidence,
                source=source,
                created_at=created_at,
                updated_at=updated_at,
                metadata=metadata,
            )
            self._fact_cache[key] = fact
            return fact

        # Actualizar el objeto existente conserva su identidad en memoria.
        fact.value = value
        fact.confidence = confidence
        fact.source = source
        fact.created_at = created_at
        fact.updated_at = updated_at
        fact.metadata = metadata

        return fact

    @_thread_safe
    def learn(
        self,
        subject: str,
        predicate: str,
        value: Any,
        *,
        confidence: float = 1.0,
        source: str = "system",
        metadata: dict[str, Any] | None = None,
    ) -> SemanticFact:
        subject = self._normalize(subject)
        predicate = self._normalize(predicate)

        if not subject:
            raise ValueError("SemanticFact subject cannot be empty.")
        if not predicate:
            raise ValueError("SemanticFact predicate cannot be empty.")

        confidence = self._normalize_confidence(confidence)
        now = datetime.now(timezone.utc).isoformat()

        current = self.get(subject, predicate)
        created_at = current.created_at.isoformat() if current else now

        metadata_value = (
            dict(metadata)
            if metadata is not None
            else (current.metadata.copy() if current else {})
        )

        value_json = json.dumps(value, ensure_ascii=False)
        metadata_json = json.dumps(metadata_value, ensure_ascii=False)

        with self._connection:
            self._connection.execute(
                """
                INSERT INTO semantic_facts
                    (
                        subject,
                        predicate,
                        value_json,
                        confidence,
                        source,
                        created_at,
                        updated_at,
                        metadata_json
                    )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(subject, predicate) DO UPDATE SET
                    value_json = excluded.value_json,
                    confidence = excluded.confidence,
                    source = excluded.source,
                    updated_at = excluded.updated_at,
                    metadata_json = excluded.metadata_json
                """,
                (
                    subject,
                    predicate,
                    value_json,
                    confidence,
                    source,
                    created_at,
                    now,
                    metadata_json,
                ),
            )

        fact = self.get(subject, predicate)
        assert fact is not None
        return fact

    @_thread_safe
    def get(
        self,
        subject: str,
        predicate: str,
    ) -> SemanticFact | None:
        row = self._connection.execute(
            """
            SELECT *
            FROM semantic_facts
            WHERE subject = ? AND predicate = ?
            """,
            (
                self._normalize(subject),
                self._normalize(predicate),
            ),
        ).fetchone()

        return self._to_fact(row)

    def get_value(
        self,
        subject: str,
        predicate: str,
        default: Any = None,
    ) -> Any:
        fact = self.get(subject, predicate)
        return default if fact is None else fact.value

    @_thread_safe
    def find_by_subject(self, subject: str) -> list[SemanticFact]:
        rows = self._connection.execute(
            """
            SELECT *
            FROM semantic_facts
            WHERE subject = ?
            ORDER BY created_at
            """,
            (self._normalize(subject),),
        ).fetchall()

        return [
            fact
            for row in rows
            if (fact := self._to_fact(row)) is not None
        ]

    @_thread_safe
    def find_by_predicate(self, predicate: str) -> list[SemanticFact]:
        rows = self._connection.execute(
            """
            SELECT *
            FROM semantic_facts
            WHERE predicate = ?
            ORDER BY created_at
            """,
            (self._normalize(predicate),),
        ).fetchall()

        return [
            fact
            for row in rows
            if (fact := self._to_fact(row)) is not None
        ]

    @_thread_safe
    def all(self) -> list[SemanticFact]:
        rows = self._connection.execute(
            """
            SELECT *
            FROM semantic_facts
            ORDER BY created_at, subject, predicate
            """
        ).fetchall()

        return [
            fact
            for row in rows
            if (fact := self._to_fact(row)) is not None
        ]

    @_thread_safe
    def count(self) -> int:
        row = self._connection.execute(
            "SELECT COUNT(*) AS total FROM semantic_facts"
        ).fetchone()

        return int(row["total"])

    @_thread_safe
    def forget(self, subject: str, predicate: str) -> bool:
        normalized_subject = self._normalize(subject)
        normalized_predicate = self._normalize(predicate)

        with self._connection:
            cursor = self._connection.execute(
                """
                DELETE FROM semantic_facts
                WHERE subject = ? AND predicate = ?
                """,
                (normalized_subject, normalized_predicate),
            )

        deleted = cursor.rowcount > 0

        if deleted:
            self._fact_cache.pop(
                (normalized_subject, normalized_predicate),
                None,
            )

        return deleted

    @_thread_safe
    def clear(self) -> None:
        with self._connection:
            self._connection.execute("DELETE FROM semantic_facts")
            self._fact_cache.clear()

    @_thread_safe
    def close(self) -> None:
        """Cierra la conexión SQLite asociada a esta instancia."""
        self._connection.close()