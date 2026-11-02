from __future__ import annotations

import argparse
import shutil
from datetime import datetime
from pathlib import Path


def replace_once(source: str, old: str, new: str, label: str) -> str:
    count = source.count(old)
    if count != 1:
        raise RuntimeError(
            f"No se pudo aplicar '{label}': se esperaba el bloque una vez y se encontró {count}. "
            "No se modificó ningún archivo."
        )
    return source.replace(old, new, 1)


def main() -> None:
    parser = argparse.ArgumentParser(description="Implementa memoria semántica mínima para NEXUS V1.")
    parser.add_argument("--root", default=".", help="Raíz del repositorio NEXUS.")
    root = Path(parser.parse_args().root).resolve()

    recognizer_path = root / "packages/planner/src/planner/intent_recognizer.py"
    engine_path = root / "packages/engine/src/engine/engine.py"
    planner_test_path = root / "packages/planner/tests/test_semantic_memory_intent.py"
    engine_test_path = root / "packages/engine/tests/test_engine_semantic_memory.py"

    missing = [str(p) for p in (recognizer_path, engine_path) if not p.is_file()]
    if missing:
        raise SystemExit("No encuentro estos archivos:\n" + "\n".join(missing) + "\nEjecutá desde la raíz de NEXUS o usá --root.")
    if planner_test_path.exists() or engine_test_path.exists():
        raise SystemExit("Ya existe uno de los archivos de prueba nuevos. Para no pisar trabajo local, no se modificó ningún archivo.")

    recognizer = recognizer_path.read_text(encoding="utf-8")
    engine = engine_path.read_text(encoding="utf-8")

    old_compound = """        compound_parts = re.split(
            r"\\s+(?:y|e|luego|después|despues|además|ademas)\\s+",
            normalized,
            maxsplit=1,
        )

        if len(compound_parts) == 2:
            first_text = compound_parts[0].strip()
            second_text = compound_parts[1].strip()

            first_intent = self._recognize_single(
                first_text,
                context,
            )

            second_intent = self._recognize_single(
                second_text,
                context,
                previous_intent=first_intent,
            )

            if (
                first_intent.action != "system.unknown"
                and second_intent.action != "system.unknown"
            ):
                return Intent(
                    action=first_intent.action,
                    confidence=min(
                        first_intent.confidence,
                        second_intent.confidence,
                    ),
                    parameters=first_intent.parameters.copy(),
                    original_text=text,
                    sub_intents=[
                        Intent(
                            action=first_intent.action,
                            confidence=first_intent.confidence,
                            parameters=first_intent.parameters.copy(),
                            original_text=first_text,
                        ),
                        Intent(
                            action=second_intent.action,
                            confidence=second_intent.confidence,
                            parameters=second_intent.parameters.copy(),
                            original_text=second_text,
                        ),
                    ],
                )
"""
    new_compound = """        # Conservamos el texto original para no perder mayúsculas
        # en valores que el usuario pide guardar.
        compound_parts = re.split(
            r"\\s+(?:y|e|luego|después|despues|además|ademas)\\s+",
            text.strip(),
            maxsplit=1,
            flags=re.IGNORECASE,
        )

        if len(compound_parts) == 2:
            first_original = compound_parts[0].strip()
            second_original = compound_parts[1].strip()
            first_text = first_original.lower()
            second_text = second_original.lower()

            first_intent = self._recognize_single(
                first_text,
                context,
                original_text=first_original,
            )

            second_intent = self._recognize_single(
                second_text,
                context,
                original_text=second_original,
                previous_intent=first_intent,
            )

            if (
                first_intent.action != "system.unknown"
                and second_intent.action != "system.unknown"
            ):
                return Intent(
                    action=first_intent.action,
                    confidence=min(
                        first_intent.confidence,
                        second_intent.confidence,
                    ),
                    parameters=first_intent.parameters.copy(),
                    original_text=text,
                    sub_intents=[
                        Intent(
                            action=first_intent.action,
                            confidence=first_intent.confidence,
                            parameters=first_intent.parameters.copy(),
                            original_text=first_original,
                        ),
                        Intent(
                            action=second_intent.action,
                            confidence=second_intent.confidence,
                            parameters=second_intent.parameters.copy(),
                            original_text=second_original,
                        ),
                    ],
                )
"""
    recognizer = replace_once(recognizer, old_compound, new_compound, "preservación del texto compuesto")

    old_episode = """        if episode_query is not None:
            return Intent(
                action="system.query_episode",
                original_text=text,
                parameters={
                    "action": episode_query.action,
                    "field": episode_query.field,
                },
            )

        #
        # Anaphoric references inside compound intents
"""
    new_episode = """        if episode_query is not None:
            return Intent(
                action="system.query_episode",
                original_text=text,
                parameters={
                    "action": episode_query.action,
                    "field": episode_query.field,
                },
            )

        #
        # Explicit semantic memory
        #
        # V1: explicit requests to remember a fact and retrieve it later.
        #
        remember_match = re.match(
            r"^(?:record[aá]|recordame|acordate|acord[aá]te|"
            r"guard[aá]|guarda|aprend[eé]|memoriz[aá])\\s+"
            r"(?:que\\s+)?(.+?)\\s+(?:se llama|es|son|está|esta)\\s+"
            r"(.+?)[.!?]*$",
            text.strip(),
            re.IGNORECASE,
        )

        if remember_match:
            predicate = re.sub(
                r"^(?:mi|mis|el|la|los|las|un|una)\\s+",
                "",
                remember_match.group(1).strip(),
                flags=re.IGNORECASE,
            )
            value = remember_match.group(2).strip().rstrip(".!?")
            if predicate and value:
                return Intent(
                    action="system.remember_fact",
                    original_text=text,
                    parameters={
                        "subject": "user",
                        "predicate": predicate.lower(),
                        "value": value,
                    },
                )

        if re.search(
            r"\\b(?:qué|que)\\s+(?:nombre|dato|información|informacion)\\s+"
            r"(?:te\\s+)?(?:ped[ií]\\s+)?(?:recordar|guardar|memorizar)\\b",
            normalized,
        ):
            return Intent(
                action="system.recall_last_fact",
                original_text=text,
                parameters={"subject": "user"},
            )

        recall_match = re.search(
            r"\\b(?:cómo|como)\\s+se\\s+llama\\s+"
            r"(?:(?:mi|mis|el|la|los|las|un|una)\\s+)?(.+?)[?!.]*$",
            normalized,
        )
        if recall_match:
            predicate = recall_match.group(1).strip()
            if predicate:
                return Intent(
                    action="system.recall_fact",
                    original_text=text,
                    parameters={
                        "subject": "user",
                        "predicate": predicate,
                    },
                )

        #
        # Anaphoric references inside compound intents
"""
    recognizer = replace_once(recognizer, old_episode, new_episode, "reconocimiento de memoria semántica")

    helper_anchor = """    async def execute(
        self,
        text: str,
    ) -> ExecutionResult:
"""
    helper_code = """    def _handle_semantic_memory_intent(
        self,
        intent,
        original_text: str,
    ) -> ExecutionResult | None:
        # Resuelve las intenciones explícitas de memoria semántica de V1.
        supported_actions = {
            "system.remember_fact",
            "system.recall_fact",
            "system.recall_last_fact",
        }
        intents = intent.sub_intents or [intent]
        # No interceptar compuestas que mezclen memoria con otras acciones.
        if not all(item.action in supported_actions for item in intents):
            return None

        operations: list[dict[str, object]] = []
        responses: list[str] = []
        for item in intents:
            parameters = item.parameters
            if item.action == "system.remember_fact":
                subject = parameters.get("subject")
                predicate = parameters.get("predicate")
                value = parameters.get("value")
                if not all(
                    isinstance(part, str) and part.strip()
                    for part in (subject, predicate, value)
                ):
                    return None
                fact = self._semantic_memory.learn(
                    subject=subject,
                    predicate=predicate,
                    value=value.strip(),
                    source="user",
                )
                responses.append(f"Recordado: {fact.predicate} = {fact.value}.")
                operations.append({
                    "action": item.action,
                    "status": "stored",
                    "subject": fact.subject,
                    "predicate": fact.predicate,
                    "value": fact.value,
                })
                continue

            if item.action == "system.recall_fact":
                subject = parameters.get("subject", "user")
                predicate = parameters.get("predicate")
                if not isinstance(subject, str) or not isinstance(predicate, str) or not predicate.strip():
                    return None
                fact = self._semantic_memory.get(subject, predicate)
                if fact is None:
                    responses.append(f"Todavía no tengo registrado ese dato: {predicate}.")
                    operations.append({"action": item.action, "status": "not_found", "predicate": predicate})
                else:
                    responses.append(f"Tengo registrado que {fact.predicate} es {fact.value}.")
                    operations.append({
                        "action": item.action,
                        "status": "found",
                        "predicate": fact.predicate,
                        "value": fact.value,
                    })
                continue

            user_facts = [
                fact for fact in self._semantic_memory.find_by_subject("user")
                if fact.source == "user"
            ]
            if not user_facts:
                responses.append("Todavía no tengo ningún dato que me hayas pedido recordar.")
                operations.append({"action": item.action, "status": "not_found"})
            else:
                fact = max(user_facts, key=lambda known_fact: known_fact.updated_at)
                responses.append(f"Me pediste recordar: {fact.predicate} = {fact.value}.")
                operations.append({
                    "action": item.action,
                    "status": "found",
                    "predicate": fact.predicate,
                    "value": fact.value,
                })

        message = " ".join(responses)
        return ExecutionResult(
            success=True,
            message=message,
            output={"operations": operations},
            metadata={"action": intent.action, "original_text": original_text, "response": message},
        )

    async def execute(
        self,
        text: str,
    ) -> ExecutionResult:
"""
    engine = replace_once(engine, helper_anchor, helper_code, "manejador de memoria del Engine")

    old_intent_log = """        self._memory.add(
            "intent",
            {
                "action": intent.action,
                "confidence": intent.confidence,
                "parameters": intent.parameters,
                "original_text": intent.original_text,
            },
        )

        #
        # ---------------------------------------------------------
        # 5. DECISION
"""
    new_intent_log = """        self._memory.add(
            "intent",
            {
                "action": intent.action,
                "confidence": intent.confidence,
                "parameters": intent.parameters,
                "original_text": intent.original_text,
            },
        )

        semantic_memory_result = self._handle_semantic_memory_intent(intent, text)
        if semantic_memory_result is not None:
            semantic_memory_result.metadata = {
                **semantic_memory_result.metadata,
                "timings": {
                    **timings,
                    "total": time.perf_counter() - total_started_at,
                },
            }
            self._memory.add(
                "execution_result",
                {
                    "success": semantic_memory_result.success,
                    "message": semantic_memory_result.message,
                    "output": semantic_memory_result.output,
                    "metadata": semantic_memory_result.metadata,
                },
            )
            self._presence_events.emit_state(
                "completed",
                message=semantic_memory_result.message,
                data={"action": intent.action},
            )
            return semantic_memory_result

        #
        # ---------------------------------------------------------
        # 5. DECISION
"""
    engine = replace_once(engine, old_intent_log, new_intent_log, "integración de memoria en Engine")

    planner_tests = """import pytest

from planner.intent_recognizer import IntentRecognizer


def test_recognizes_explicit_memory_write_and_preserves_value_case() -> None:
    intent = IntentRecognizer().recognize("Recordá que mi proyecto actual se llama NEXUS.")
    assert intent.action == "system.remember_fact"
    assert intent.parameters == {
        "subject": "user",
        "predicate": "proyecto actual",
        "value": "NEXUS",
    }


def test_recognizes_semantic_memory_lookup() -> None:
    intent = IntentRecognizer().recognize("¿Cómo se llama mi proyecto actual?")
    assert intent.action == "system.recall_fact"
    assert intent.parameters == {"subject": "user", "predicate": "proyecto actual"}


def test_recognizes_compound_remember_and_recall_last_fact() -> None:
    intent = IntentRecognizer().recognize(
        "Recordá que mi proyecto actual se llama NEXUS y después decime qué nombre te pedí recordar"
    )
    assert intent.is_compound
    assert [part.action for part in intent.sub_intents] == [
        "system.remember_fact",
        "system.recall_last_fact",
    ]
    assert intent.sub_intents[0].parameters["value"] == "NEXUS"
"""

    engine_tests = """from unittest.mock import AsyncMock, MagicMock

import pytest

from engine.engine import Engine
from planner.intent_recognizer import IntentRecognizer
from runtime.runtime import Runtime


def build_engine() -> Engine:
    runtime = MagicMock(spec=Runtime)
    runtime.tool_registry = MagicMock()
    runtime.tool_registry.describe.return_value = []
    runtime.tool_registry.resolve = MagicMock()
    recognizer = IntentRecognizer()
    intent_provider = MagicMock()
    intent_provider.recognize = AsyncMock(
        side_effect=lambda text, _capabilities, context: recognizer.recognize(text, context)
    )
    return Engine(runtime=runtime, intent_provider=intent_provider)


@pytest.mark.asyncio
async def test_engine_remembers_and_recalls_a_fact() -> None:
    engine = build_engine()
    stored = await engine.execute("Recordá que mi proyecto actual se llama NEXUS.")
    recalled = await engine.execute("¿Cómo se llama mi proyecto actual?")
    assert stored.success
    assert "NEXUS" in stored.message
    assert recalled.success
    assert "NEXUS" in recalled.message
    assert engine.semantic_memory.get_value("user", "proyecto actual") == "NEXUS"


@pytest.mark.asyncio
async def test_engine_executes_compound_remember_and_recall() -> None:
    engine = build_engine()
    result = await engine.execute(
        "Recordá que mi proyecto actual se llama NEXUS y después decime qué nombre te pedí recordar"
    )
    assert result.success
    assert "NEXUS" in result.message
    assert engine.semantic_memory.get_value("user", "proyecto actual") == "NEXUS"
"""

    for source, path in ((recognizer, recognizer_path), (engine, engine_path), (planner_tests, planner_test_path), (engine_tests, engine_test_path)):
        compile(source, str(path), "exec")

    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    backups = {}
    for path in (recognizer_path, engine_path):
        backup = path.with_name(f"{path.name}.bak-{timestamp}")
        shutil.copy2(path, backup)
        backups[path] = backup
    try:
        recognizer_path.write_text(recognizer, encoding="utf-8")
        engine_path.write_text(engine, encoding="utf-8")
        planner_test_path.parent.mkdir(parents=True, exist_ok=True)
        engine_test_path.parent.mkdir(parents=True, exist_ok=True)
        planner_test_path.write_text(planner_tests, encoding="utf-8")
        engine_test_path.write_text(engine_tests, encoding="utf-8")
    except Exception:
        for path, backup in backups.items():
            shutil.copy2(backup, path)
        for path in (planner_test_path, engine_test_path):
            if path.exists():
                path.unlink()
        raise

    print("Cambios aplicados. Copias de seguridad creadas:")
    for path, backup in backups.items():
        print(f"  {path.relative_to(root)} -> {backup.name}")
    print("Pruebas nuevas:")
    print(f"  {planner_test_path.relative_to(root)}")
    print(f"  {engine_test_path.relative_to(root)}")
    print("Ahora ejecutá las dos pruebas nuevas; no se corrió una batería general.")


if __name__ == "__main__":
    main()
