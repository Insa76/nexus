from pathlib import Path
from datetime import datetime
import shutil
import re

ROOT = Path.cwd()
MEMORY = ROOT / 'packages/memory/src/memory/semantic_memory.py'
ENGINE = ROOT / 'packages/engine/src/engine/engine.py'
BOOTSTRAP = ROOT / 'packages/bootstrap/src/bootstrap/bootstrap.py'

for p in (MEMORY, ENGINE, BOOTSTRAP):
    if not p.is_file():
        raise SystemExit(f'No se encontró el archivo esperado: {p}')

memory_text = MEMORY.read_text(encoding='utf-8')
engine_text = ENGINE.read_text(encoding='utf-8')
bootstrap_text = BOOTSTRAP.read_text(encoding='utf-8')

# Guard against applying this patch twice.
if 'import sqlite3' in memory_text and 'NEXUS_SEMANTIC_MEMORY_PATCH_V1' in memory_text:
    raise SystemExit('La persistencia semántica ya parece estar aplicada. No se modificó ningún archivo.')
if 'semantic_memory: SemanticMemory | None = None' in engine_text:
    raise SystemExit('Engine ya acepta semantic_memory. No se modificó ningún archivo.')
if 'NEXUS_SEMANTIC_MEMORY_DB_PATH' in bootstrap_text:
    raise SystemExit('Bootstrap ya configura NEXUS_SEMANTIC_MEMORY_DB_PATH. No se modificó ningún archivo.')

# Full implementation retains the existing public API and uses SQLite.
new_memory = '''from __future__ import annotations

import json
import sqlite3
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


@dataclass
class SemanticFact:
    """Representa una unidad de conocimiento semántico reutilizable."""

    subject: str
    predicate: str
    value: Any
    confidence: float = 1.0
    source: str = "system"
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: dict[str, Any] = field(default_factory=dict)


class SemanticMemory:
    """Memoria semántica con persistencia SQLite opcional.

    Si db_path es None, usa una base SQLite en memoria (apropiada para tests).
    Para persistencia entre reinicios, se debe proporcionar una ruta de archivo.
    """

    # NEXUS_SEMANTIC_MEMORY_PATCH_V1
    def __init__(self, db_path: str | Path | None = None) -> None:
        if db_path is None or str(db_path) == ":memory:":
            resolved_path = ":memory:"
        else:
            path = Path(db_path).expanduser()
            path.parent.mkdir(parents=True, exist_ok=True)
            resolved_path = str(path)

        self._connection = sqlite3.connect(resolved_path, timeout=10.0)
        self._connection.row_factory = sqlite3.Row
        self._connection.execute("PRAGMA foreign_keys = ON")
        if resolved_path != ":memory:":
            self._connection.execute("PRAGMA journal_mode = WAL")
        self._initialize_schema()

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
            raise ValueError("SemanticFact confidence must be numeric.") from exc
        return max(0.0, min(1.0, confidence))

    @staticmethod
    def _to_fact(row: sqlite3.Row | None) -> SemanticFact | None:
        if row is None:
            return None
        return SemanticFact(
            subject=row["subject"],
            predicate=row["predicate"],
            value=json.loads(row["value_json"]),
            confidence=float(row["confidence"]),
            source=row["source"],
            created_at=datetime.fromisoformat(row["created_at"]),
            updated_at=datetime.fromisoformat(row["updated_at"]),
            metadata=json.loads(row["metadata_json"]),
        )

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
        metadata_value = dict(metadata) if metadata is not None else (current.metadata if current else {})

        value_json = json.dumps(value, ensure_ascii=False)
        metadata_json = json.dumps(metadata_value, ensure_ascii=False)
        with self._connection:
            self._connection.execute(
                """
                INSERT INTO semantic_facts
                    (subject, predicate, value_json, confidence, source,
                     created_at, updated_at, metadata_json)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(subject, predicate) DO UPDATE SET
                    value_json = excluded.value_json,
                    confidence = excluded.confidence,
                    source = excluded.source,
                    updated_at = excluded.updated_at,
                    metadata_json = excluded.metadata_json
                """,
                (subject, predicate, value_json, confidence, source,
                 created_at, now, metadata_json),
            )
        fact = self.get(subject, predicate)
        assert fact is not None
        return fact

    def get(self, subject: str, predicate: str) -> SemanticFact | None:
        row = self._connection.execute(
            "SELECT * FROM semantic_facts WHERE subject = ? AND predicate = ?",
            (self._normalize(subject), self._normalize(predicate)),
        ).fetchone()
        return self._to_fact(row)

    def get_value(self, subject: str, predicate: str, default: Any = None) -> Any:
        fact = self.get(subject, predicate)
        return default if fact is None else fact.value

    def find_by_subject(self, subject: str) -> list[SemanticFact]:
        rows = self._connection.execute(
            "SELECT * FROM semantic_facts WHERE subject = ? ORDER BY created_at",
            (self._normalize(subject),),
        ).fetchall()
        return [fact for row in rows if (fact := self._to_fact(row)) is not None]

    def find_by_predicate(self, predicate: str) -> list[SemanticFact]:
        rows = self._connection.execute(
            "SELECT * FROM semantic_facts WHERE predicate = ? ORDER BY created_at",
            (self._normalize(predicate),),
        ).fetchall()
        return [fact for row in rows if (fact := self._to_fact(row)) is not None]

    def all(self) -> list[SemanticFact]:
        rows = self._connection.execute(
            "SELECT * FROM semantic_facts ORDER BY created_at, subject, predicate"
        ).fetchall()
        return [fact for row in rows if (fact := self._to_fact(row)) is not None]

    def count(self) -> int:
        row = self._connection.execute(
            "SELECT COUNT(*) AS total FROM semantic_facts"
        ).fetchone()
        return int(row["total"])

    def forget(self, subject: str, predicate: str) -> bool:
        with self._connection:
            cursor = self._connection.execute(
                "DELETE FROM semantic_facts WHERE subject = ? AND predicate = ?",
                (self._normalize(subject), self._normalize(predicate)),
            )
        return cursor.rowcount > 0

    def clear(self) -> None:
        with self._connection:
            self._connection.execute("DELETE FROM semantic_facts")

    def close(self) -> None:
        """Cierra la conexión SQLite asociada a esta instancia."""
        self._connection.close()
'''

# Inject optional memory dependency into Engine without changing existing callers.
old_sig = '    default_actor_type: str | None = None,\n) -> None:\n'
new_sig = '    default_actor_type: str | None = None,\n    semantic_memory: SemanticMemory | None = None,\n) -> None:\n'
if engine_text.count(old_sig) != 1:
    raise SystemExit('No se pudo identificar de forma única la firma de Engine; no se modificó ningún archivo.')
engine_new = engine_text.replace(old_sig, new_sig, 1)
old_instance = '        self._semantic_memory = SemanticMemory()\n'
new_instance = '        self._semantic_memory = semantic_memory if semantic_memory is not None else SemanticMemory()\n'
if engine_new.count(old_instance) != 1:
    raise SystemExit('No se pudo identificar de forma única la inicialización de SemanticMemory; no se modificó ningún archivo.')
engine_new = engine_new.replace(old_instance, new_instance, 1)

# Bootstrap creates the persistent instance at the normal application entry point.
if 'from engine.engine import Engine' not in bootstrap_text:
    raise SystemExit('No se encontró el import de Engine en bootstrap; no se modificó ningún archivo.')
bootstrap_new = bootstrap_text.replace(
    'from engine.engine import Engine',
    'from engine.engine import Engine\nfrom memory.semantic_memory import SemanticMemory',
    1,
)
old_return = '    return Engine(\n        runtime,\n        intent_provider=intent_provider,\n'
new_return = '''    semantic_memory_db_path = os.environ.get(
        "NEXUS_SEMANTIC_MEMORY_DB_PATH",
        str(Path.home() / ".nexus" / "semantic_memory.db"),
    )
    semantic_memory = SemanticMemory(db_path=semantic_memory_db_path)

    return Engine(
        runtime,
        intent_provider=intent_provider,
        semantic_memory=semantic_memory,
'''
if bootstrap_new.count(old_return) != 1:
    raise SystemExit('No se pudo identificar de forma única el retorno Engine de build_engine; no se modificó ningún archivo.')
bootstrap_new = bootstrap_new.replace(old_return, new_return, 1)

# All validation completed; back up and write the three files.
for p, old in ((MEMORY, memory_text), (ENGINE, engine_text), (BOOTSTRAP, bootstrap_text)):
    stamp = datetime.now().strftime('%Y%m%d-%H%M%S')
    backup = p.with_name(p.name + f'.bak-semantic-persistence-{stamp}')
    shutil.copy2(p, backup)

MEMORY.write_text(new_memory, encoding='utf-8')
ENGINE.write_text(engine_new, encoding='utf-8')
BOOTSTRAP.write_text(bootstrap_new, encoding='utf-8')

# Add isolated unit tests for persistence behavior.
tests_dir = ROOT / 'packages/memory/tests'
tests_dir.mkdir(parents=True, exist_ok=True)
test_file = tests_dir / 'test_semantic_memory_persistence.py'
if test_file.exists():
    raise SystemExit(f'Se modificaron los tres archivos principales, pero ya existía {test_file}; no se sobrescribió el test.')
test_file.write_text('''from pathlib import Path\n\nfrom memory.semantic_memory import SemanticMemory\n\n\ndef test_semantic_memory_persists_facts_after_reopen(tmp_path: Path) -> None:\n    db_path = tmp_path / "semantic.db"\n    first = SemanticMemory(db_path=db_path)\n    first.learn("User", "Favorite color", "blue", metadata={"source": "test"})\n    first.close()\n\n    second = SemanticMemory(db_path=db_path)\n    fact = second.get("user", "favorite color")\n    assert fact is not None\n    assert fact.value == "blue"\n    assert fact.metadata == {"source": "test"}\n    second.close()\n\n\ndef test_semantic_memory_updates_and_forgets_persistently(tmp_path: Path) -> None:\n    db_path = tmp_path / "semantic.db"\n    memory = SemanticMemory(db_path=db_path)\n    memory.learn("user", "favorite color", "blue")\n    memory.learn("user", "favorite color", "green")\n    assert memory.get_value("user", "favorite color") == "green"\n    assert memory.forget("user", "favorite color") is True\n    assert memory.get_value("user", "favorite color") is None\n    assert memory.forget("user", "favorite color") is False\n    memory.close()\n\n\ndef test_semantic_memory_clear_removes_persisted_facts(tmp_path: Path) -> None:\n    db_path = tmp_path / "semantic.db"\n    memory = SemanticMemory(db_path=db_path)\n    memory.learn("user", "project", "NEXUS")\n    memory.clear()\n    assert memory.count() == 0\n    memory.close()\n\n    reopened = SemanticMemory(db_path=db_path)\n    assert reopened.count() == 0\n    reopened.close()\n''', encoding='utf-8')

print('Persistencia semántica aplicada correctamente.')
print('Archivos modificados:')
for p in (MEMORY, ENGINE, BOOTSTRAP, test_file):
    print(f'  {p}')
print('Se crearon copias .bak-semantic-persistence-* de los tres archivos originales.')
print('La memoria de Engine fuera de bootstrap sigue siendo SQLite en memoria; build_engine() usa ~/.nexus/semantic_memory.db por defecto.')
