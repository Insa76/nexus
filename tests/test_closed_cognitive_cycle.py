from __future__ import annotations

import asyncio

from engine.engine import Engine
from memory import WorkingMemory
from planner.intent import Intent
from planner.intent_provider import IntentProvider
from planner.plan import StepStatus
from runtime.execution_result import ExecutionResult


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
                "name": "windows.close_app",
                "action": "system.close_app",
                "description": "Close application",
                "provider": "windows",
                "parameters": {
                    "application": {
                        "type": "string",
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
    """
    Runtime mínimo para probar el ciclo cognitivo completo.

    Reproduce la evidencia estructural que el Runtime real
    entrega al Verifier después de una ejecución.
    """

    def __init__(self):
        self.tool_registry = FakeToolRegistry()
        self.action_registry = FakeActionRegistry()
        self.executions = []

    async def execute(self, context):
        self.executions.append(
            context.objective.metadata.copy()
        )

        application = (
            context.objective.metadata.get(
                "application"
            )
        )

        action = context.objective.title

        if action == "system.open_app":
            output = {
                "status": "opened",
                "application": application,
            }
        elif action == "system.close_app":
            output = {
                "status": "closed",
                "application": application,
            }
        else:
            output = {
                "status": "completed",
                "action": action,
            }

        for step in context.plan.steps:
            step.status = StepStatus.COMPLETED

            step.metadata["execution"] = {
                "status": "completed",
                "result_keys": list(
                    output.keys()
                ),
                "artifact_keys": [],
            }

        context.plan.completed = True

        return ExecutionResult(
            success=True,
            message="",
            output=output,
            artifacts={},
            metadata={},
        )


class RecordingIntentProvider(IntentProvider):
    """
    Devuelve intents predefinidos y conserva todos los contextos
    que recibe para comprobar qué conocimiento llega al segundo ciclo.
    """

    def __init__(self, intents):
        self.intents = list(intents)
        self.calls = []

    async def recognize(
        self,
        text,
        capabilities=None,
        context=None,
    ):
        self.calls.append(
            {
                "text": text,
                "capabilities": capabilities,
                "context": context,
            }
        )

        if not self.intents:
            raise AssertionError(
                "No more fake intents are available."
            )

        return self.intents.pop(0)


def run(coro):
    return asyncio.run(coro)


def check(condition, message):
    if not condition:
        raise AssertionError(message)


def test_closed_cognitive_cycle():
    """
    Demuestra el ciclo:

        REQUEST 1
            ↓
        EXECUTE
            ↓
        VERIFY
            ↓
        LEARN
            ↓
        SEMANTIC MEMORY
            ↓
        REQUEST 2
            ↓
        CONTEXT
            ↓
        INTENT

    La segunda solicitud debe recibir conocimiento
    derivado de la primera experiencia verificada.
    """

    first_intent = Intent(
        action="system.open_app",
        confidence=1.0,
        parameters={
            "application": "Chrome",
        },
        original_text="Abrí Chrome",
    )

    second_intent = Intent(
        action="system.close_app",
        confidence=1.0,
        parameters={
            "application": "Chrome",
        },
        original_text="Cerrá la aplicación",
    )

    runtime = FakeRuntime()

    intent_provider = RecordingIntentProvider(
        [
            first_intent,
            second_intent,
        ]
    )

    engine = Engine(
        runtime=runtime,
        intent_provider=intent_provider,
        memory=WorkingMemory(),
    )

    #
    # ---------------------------------------------------------
    # CICLO 1
    # ---------------------------------------------------------
    #

    first_result = run(
        engine.execute("Abrí Chrome")
    )

    check(
        first_result.success,
        "First execution should succeed.",
    )

    check(
        first_result.metadata["verification"]["verified"],
        "First execution must be verified.",
    )

    #
    # ---------------------------------------------------------
    # LEARNING
    # ---------------------------------------------------------
    #

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
        "Semantic knowledge must preserve episode provenance.",
    )

    #
    # ---------------------------------------------------------
    # EPISODIC MEMORY
    # ---------------------------------------------------------
    #

    episodes = engine.memory.find(
        "episode"
    )

    check(
        len(episodes) >= 1,
        "Verified execution must reach episodic memory.",
    )

    #
    # ---------------------------------------------------------
    # CICLO 2
    # ---------------------------------------------------------
    #

    second_result = run(
        engine.execute("Cerrá la aplicación")
    )

    check(
        second_result.success,
        "Second execution should succeed.",
    )

    check(
        second_result.metadata["verification"]["verified"],
        "Second execution must also be verified.",
    )

    #
    # ---------------------------------------------------------
    # CONTEXT RECEIVED BY INTENT PROVIDER
    # ---------------------------------------------------------
    #

    check(
        len(intent_provider.calls) == 2,
        "IntentProvider must have received two requests.",
    )

    second_call = intent_provider.calls[1]

    second_context = second_call["context"]

    check(
        isinstance(second_context, dict),
        "Second request must receive a cognitive context.",
    )

    #
    # The semantic fact learned from the first execution
    # must be available to the second cognitive cycle.
    #
    semantic_knowledge = second_context.get(
        "semantic_knowledge"
    )

    check(
        semantic_knowledge is not None,
        (
            "Second cognitive cycle must receive "
            "semantic knowledge from the first cycle."
        ),
    )

    #
    # Accept either a single fact representation or a list
    # of facts, while keeping the assertion deterministic.
    #
    if isinstance(
        semantic_knowledge,
        list,
    ):
        matching_fact = any(
            isinstance(item, dict)
            and item.get("subject") == "chrome"
            and item.get("predicate")
            == "es una aplicación"
            and item.get("value") is True
            for item in semantic_knowledge
        )
    elif isinstance(
        semantic_knowledge,
        dict,
    ):
        matching_fact = (
            semantic_knowledge.get("subject")
            == "chrome"
            and semantic_knowledge.get("predicate")
            == "es una aplicación"
            and semantic_knowledge.get("value")
            is True
        )
    else:
        matching_fact = False

    check(
        matching_fact,
        (
            "Second cognitive cycle must receive "
            "the learned Chrome semantic fact."
        ),
    )

    #
    # ---------------------------------------------------------
    # NEXT DECISION
    # ---------------------------------------------------------
    #

    decision_entries = engine.memory.find(
        "decision"
    )

    check(
        len(decision_entries) == 2,
        "Both requests must reach the DecisionEngine.",
    )

    check(
        decision_entries[0].data[
            "selected_action"
        ]
        == "system.open_app",
        "First decision must select system.open_app.",
    )

    check(
        decision_entries[1].data[
            "selected_action"
        ]
        == "system.close_app",
        "Second decision must select system.close_app.",
    )

    #
    # ---------------------------------------------------------
    # FINAL ASSERTION
    # ---------------------------------------------------------
    #

    print(
        "CLOSED COGNITIVE CYCLE"
    )
    print(
        "============================================================"
    )
    print(
        "PASSED : 1"
    )
    print(
        "FAILED : 0"
    )


if __name__ == "__main__":
    try:
        test_closed_cognitive_cycle()
    except Exception as exc:
        print(
            "CLOSED COGNITIVE CYCLE"
        )
        print(
            "============================================================"
        )
        print(
            "PASSED : 0"
        )
        print(
            "FAILED : 1"
        )
        print(
            f"ERROR  : {exc}"
        )
        raise
