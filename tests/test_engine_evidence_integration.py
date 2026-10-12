from __future__ import annotations

import asyncio

from engine.engine import Engine
from memory import WorkingMemory
from planner.intent import Intent
from planner.intent_provider import IntentProvider
from runtime.execution_result import ExecutionResult
from planner.plan import StepStatus


class FakeToolRegistry:

    def describe(self):
        return [
            {
                "name": "windows.open_app",
                "action": "system.open_app",
                "description": "Open application",
                "provider": "windows",
                "parameters": {
                    "application": {
                        "type": "string",
                        "required": True,
                    }
                },
            },
            {
                "name": "windows.set_volume",
                "action": "system.set_volume",
                "description": "Set volume",
                "provider": "windows",
                "parameters": {
                    "level": {
                        "type": "number",
                        "required": True,
                    }
                },
            },
        ]

    def resolve(self, action):
        return object()


class FakeAction:

    def __init__(self, name):
        self.name = name
        self.internal = False


class FakeActionRegistry:

    def get(self, action):
        return FakeAction(action)


class FakeRuntime:

    def __init__(self, result):
        self.tool_registry = FakeToolRegistry()
        self.action_registry = FakeActionRegistry()
        self.result = result

    async def execute(self, context):
        """
        Simula el resultado final del runtime real.

        Como este FakeRuntime no atraviesa ActionManager,
        reproduce explícitamente la evidencia estructural
        que ActionManager registra durante una ejecución real.
        """

        result_output = (
            self.result.output
            if isinstance(self.result.output, dict)
            else {}
        )

        result_artifacts = (
            self.result.artifacts
            if isinstance(self.result.artifacts, dict)
            else {}
        )

        result_keys = list(result_output.keys())
        artifact_keys = list(result_artifacts.keys())

        for step in context.plan.steps:

            step.status = StepStatus.COMPLETED

            step.metadata["execution"] = {
                "status": "completed",
                "result_keys": result_keys,
                "artifact_keys": artifact_keys,
            }

        context.plan.completed = True

        return self.result


class FakeIntentProvider(IntentProvider):

    def __init__(self, intent):
        self.intent = intent

    async def recognize(
        self,
        text,
        capabilities=None,
        context=None,
    ):
        return self.intent


def run(coro):
    return asyncio.run(coro)


def check(condition, message):
    if not condition:
        raise AssertionError(message)


def test_engine_open_app_evidence_verified():

    intent = Intent(
        action="system.open_app",
        confidence=1.0,
        parameters={
            "application": "Chrome",
        },
        original_text="Abrí Chrome",
    )

    runtime = FakeRuntime(
        ExecutionResult(
            success=True,
            message="",
            output={
                "application": "Chrome",
                "status": "opened",
            },
            artifacts={},
            metadata={},
        )
    )

    engine = Engine(
        runtime=runtime,
        intent_provider=FakeIntentProvider(intent),
        memory=WorkingMemory(),
    )

    result = run(
        engine.execute("Abrí Chrome")
    )

    check(
        result.success,
        "Execution should succeed.",
    )

    check(
        result.metadata["verification"]["verified"],
        "Engine should mark matching evidence as verified.",
    )

    check(
        result.metadata["verification"]["confidence"] == 1.0,
        "Verified evidence should have confidence 1.0.",
    )


def test_engine_open_app_evidence_mismatch():

    intent = Intent(
        action="system.open_app",
        confidence=1.0,
        parameters={
            "application": "Chrome",
        },
        original_text="Abrí Chrome",
    )

    runtime = FakeRuntime(
        ExecutionResult(
            success=True,
            message="",
            output={
                "application": "Spotify",
                "status": "opened",
            },
            artifacts={},
            metadata={},
        )
    )

    engine = Engine(
        runtime=runtime,
        intent_provider=FakeIntentProvider(intent),
        memory=WorkingMemory(),
    )

    result = run(
        engine.execute("Abrí Chrome")
    )

    check(
        result.success,
        "Execution itself should succeed.",
    )

    check(
        not result.metadata["verification"]["verified"],
        "Mismatching evidence must not be verified.",
    )

    verification_entries = engine.memory.find(
        "verification_failure"
    )

    check(
        len(verification_entries) == 1,
        "Verification failure should be stored in memory.",
    )


def test_engine_volume_evidence_verified():

    intent = Intent(
        action="system.set_volume",
        confidence=1.0,
        parameters={
            "level": 50,
        },
        original_text="Poné el volumen al 50%",
    )

    runtime = FakeRuntime(
        ExecutionResult(
            success=True,
            message="",
            output={
                "volume": 50,
                "status": "set",
            },
            artifacts={},
            metadata={},
        )
    )

    engine = Engine(
        runtime=runtime,
        intent_provider=FakeIntentProvider(intent),
        memory=WorkingMemory(),
    )

    result = run(
        engine.execute(
            "Poné el volumen al 50%"
        )
    )

    check(
        result.metadata["verification"]["verified"],
        "Matching volume evidence should be verified.",
    )


def test_engine_volume_evidence_mismatch():

    intent = Intent(
        action="system.set_volume",
        confidence=1.0,
        parameters={
            "level": 50,
        },
        original_text="Poné el volumen al 50%",
    )

    runtime = FakeRuntime(
        ExecutionResult(
            success=True,
            message="",
            output={
                "volume": 30,
                "status": "set",
            },
            artifacts={},
            metadata={},
        )
    )

    engine = Engine(
        runtime=runtime,
        intent_provider=FakeIntentProvider(intent),
        memory=WorkingMemory(),
    )

    result = run(
        engine.execute(
            "Poné el volumen al 50%"
        )
    )

    check(
        not result.metadata["verification"]["verified"],
        "Wrong volume evidence must not be verified.",
    )

    verification_entries = engine.memory.find(
        "verification_failure"
    )

    check(
        len(verification_entries) == 1,
        "Volume verification failure should be stored.",
    )


def test_engine_verification_is_stored_in_memory():

    intent = Intent(
        action="system.open_app",
        confidence=1.0,
        parameters={
            "application": "Chrome",
        },
        original_text="Abrí Chrome",
    )

    runtime = FakeRuntime(
        ExecutionResult(
            success=True,
            message="",
            output={
                "application": "Chrome",
                "status": "opened",
            },
            artifacts={},
            metadata={},
        )
    )

    engine = Engine(
        runtime=runtime,
        intent_provider=FakeIntentProvider(intent),
        memory=WorkingMemory(),
    )

    run(
        engine.execute("Abrí Chrome")
    )

    entries = engine.memory.find(
        "verification"
    )

    check(
        len(entries) == 1,
        "Verification must be stored in WorkingMemory.",
    )

    verification = entries[0].data

    check(
        verification["verified"] is True,
        "Stored verification must be true.",
    )

    check(
        verification["confidence"] == 1.0,
        "Stored verification confidence must be 1.0.",
    )


def test_engine_verification_metadata_contains_evidence():

    intent = Intent(
        action="system.open_app",
        confidence=1.0,
        parameters={
            "application": "Chrome",
        },
        original_text="Abrí Chrome",
    )

    runtime = FakeRuntime(
        ExecutionResult(
            success=True,
            message="",
            output={
                "application": "Chrome",
                "status": "opened",
            },
            artifacts={},
            metadata={},
        )
    )

    engine = Engine(
        runtime=runtime,
        intent_provider=FakeIntentProvider(intent),
        memory=WorkingMemory(),
    )

    result = run(
        engine.execute("Abrí Chrome")
    )

    verification = result.metadata[
        "verification"
    ]

    check(
        verification["verified"] is True,
        "Verification must be true.",
    )

    check(
        len(verification["evidence"]) >= 1,
        "Verification must expose evidence.",
    )

    check(
        any(
            item.get("type") == "state"
            for item in verification["evidence"]
        ),
        "State evidence must be present.",
    )


def test_engine_failed_execution_never_reaches_verified():

    intent = Intent(
        action="system.open_app",
        confidence=1.0,
        parameters={
            "application": "Chrome",
        },
        original_text="Abrí Chrome",
    )

    runtime = FakeRuntime(
        ExecutionResult(
            success=False,
            message="No se pudo abrir Chrome.",
            output={},
            artifacts={},
            metadata={},
        )
    )

    engine = Engine(
        runtime=runtime,
        intent_provider=FakeIntentProvider(intent),
        memory=WorkingMemory(),
    )

    result = run(
        engine.execute("Abrí Chrome")
    )

    check(
        not result.success,
        "Execution should fail.",
    )

    #
    # En una ejecución fallida el Engine debe conservar
    # la frontera de verificación.
    #

    verification_entries = engine.memory.find(
        "verification"
    )

    check(
        len(verification_entries) == 1,
        "Verification should still be recorded.",
    )

    check(
        verification_entries[0].data["verified"] is False,
        "Failed execution must not be verified.",
    )


def test_engine_only_verified_execution_can_be_learned():

    intent = Intent(
        action="system.open_app",
        confidence=1.0,
        parameters={
            "application": "Chrome",
        },
        original_text="Abrí Chrome",
    )

    runtime = FakeRuntime(
        ExecutionResult(
            success=True,
            message="",
            output={
                "application": "Chrome",
                "status": "opened",
            },
            artifacts={},
            metadata={},
        )
    )

    engine = Engine(
        runtime=runtime,
        intent_provider=FakeIntentProvider(intent),
        memory=WorkingMemory(),
    )

    result = run(
        engine.execute("Abrí Chrome")
    )

    check(
        result.metadata["verification"]["verified"],
        "Execution must be verified.",
    )

    semantic_fact = engine.semantic_memory.get(
        "chrome",
        "es una aplicación",
    )

    check(
        semantic_fact is not None,
        "Verified execution must create semantic knowledge.",
    )

    check(
        semantic_fact.value is True,
        "Learned application fact must be true.",
    )

    check(
        semantic_fact.source == "episode",
        "Learned knowledge must preserve episode provenance.",
    )


def test_engine_unverified_execution_is_not_learned():

    intent = Intent(
        action="system.open_app",
        confidence=1.0,
        parameters={
            "application": "Chrome",
        },
        original_text="Abrí Chrome",
    )

    runtime = FakeRuntime(
        ExecutionResult(
            success=True,
            message="",
            output={
                "application": "Spotify",
                "status": "opened",
            },
            artifacts={},
            metadata={},
        )
    )

    engine = Engine(
        runtime=runtime,
        intent_provider=FakeIntentProvider(intent),
        memory=WorkingMemory(),
    )

    result = run(
        engine.execute("Abrí Chrome")
    )

    check(
        not result.metadata["verification"]["verified"],
        "Mismatching evidence must not be verified.",
    )

    semantic_fact = engine.semantic_memory.get(
        "chrome",
        "es una aplicación",
    )

    check(
        semantic_fact is None,
        "Unverified execution must not create semantic knowledge.",
    )

    check(
        engine.semantic_memory.count() == 0,
        "Semantic memory must remain empty after failed verification.",
    )


if __name__ == "__main__":

    tests = [
        test_engine_open_app_evidence_verified,
        test_engine_open_app_evidence_mismatch,
        test_engine_volume_evidence_verified,
        test_engine_volume_evidence_mismatch,
        test_engine_verification_is_stored_in_memory,
        test_engine_verification_metadata_contains_evidence,
        test_engine_failed_execution_never_reaches_verified,
        test_engine_only_verified_execution_can_be_learned,
        test_engine_unverified_execution_is_not_learned,
    ]

    passed = 0

    for test in tests:
        test()
        passed += 1

    print("=" * 72)
    print("ENGINE EVIDENCE + LEARNING INTEGRATION")
    print("=" * 72)
    print(f"PASSED : {passed}")
    print(f"FAILED : {len(tests) - passed}")
    print("=" * 72)
