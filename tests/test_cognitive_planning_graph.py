from __future__ import annotations

from planner.intent import Intent
from planner.objective import (
    Objective,
    ObjectiveStatus,
)
from planner.planner import Planner


class FakeTool:

    def __init__(
        self,
        *,
        produces=None,
        consumes=None,
    ):
        self.produces = list(
            produces or []
        )
        self.consumes = list(
            consumes or []
        )


class FakeToolRegistry:

    def __init__(self, tools):
        self.tools = tools

    def resolve(self, action):
        return self.tools.get(action)


def make_objective(
    objective_id="objective-1",
):
    return Objective(
        id=objective_id,
        title="test",
        description="test objective",
    )


def test_linear_dependency_chain_is_valid():

    registry = FakeToolRegistry(
        {
            "system.capture": FakeTool(
                produces=["image"],
            ),
            "system.inspect": FakeTool(
                consumes=["image"],
                produces=["inspection"],
            ),
            "system.process": FakeTool(
                consumes=["inspection"],
                produces=["result"],
            ),
        }
    )

    planner = Planner(
        tool_resolver=registry.resolve
    )

    objective = make_objective()

    capture = Intent(
        action="system.capture",
        original_text="capturar",
    )

    inspect_capture = Intent(
        action="system.inspect",
        original_text="inspeccionar",
    )

    process = Intent(
        action="system.process",
        original_text="procesar",
    )

    intent = Intent(
        action=capture.action,
        original_text="capturar, inspeccionar y procesar",
        sub_intents=[
            capture,
            inspect_capture,
            process,
        ],
    )

    plan = planner.create_plan(
        objective,
        intent,
    )

    assert (
        objective.status
        == ObjectiveStatus.READY
    )

    assert (
        plan.steps[1].depends_on
        == [plan.steps[0].id]
    )

    assert (
        plan.steps[2].depends_on
        == [plan.steps[1].id]
    )


def test_dependency_graph_can_branch():

    registry = FakeToolRegistry(
        {
            "system.capture": FakeTool(
                produces=["image"],
            ),
            "system.inspect": FakeTool(
                consumes=["image"],
                produces=["inspection"],
            ),
            "system.archive": FakeTool(
                consumes=["image"],
                produces=["archive"],
            ),
        }
    )

    planner = Planner(
        tool_resolver=registry.resolve
    )

    objective = make_objective()

    capture = Intent(
        action="system.capture",
        original_text="capturar",
    )

    inspect_capture = Intent(
        action="system.inspect",
        original_text="inspeccionar",
    )

    archive = Intent(
        action="system.archive",
        original_text="archivar",
    )

    intent = Intent(
        action=capture.action,
        original_text="capturar, inspeccionar y archivar",
        sub_intents=[
            capture,
            inspect_capture,
            archive,
        ],
    )

    plan = planner.create_plan(
        objective,
        intent,
    )

    assert (
        objective.status
        == ObjectiveStatus.READY
    )

    assert (
        plan.steps[1].depends_on
        == [plan.steps[0].id]
    )

    assert (
        plan.steps[2].depends_on
        == [plan.steps[0].id]
    )


def test_independent_steps_can_coexist_with_dependency_graph():

    registry = FakeToolRegistry(
        {
            "system.capture": FakeTool(
                produces=["image"],
            ),
            "system.inspect": FakeTool(
                consumes=["image"],
                produces=["inspection"],
            ),
            "system.open": FakeTool(
                produces=["application_opened"],
            ),
        }
    )

    planner = Planner(
        tool_resolver=registry.resolve
    )

    objective = make_objective()

    capture = Intent(
        action="system.capture",
        original_text="capturar",
    )

    inspect_capture = Intent(
        action="system.inspect",
        original_text="inspeccionar",
    )

    open_app = Intent(
        action="system.open",
        original_text="abrir aplicación",
    )

    intent = Intent(
        action=capture.action,
        original_text="capturar, inspeccionar y abrir",
        sub_intents=[
            capture,
            inspect_capture,
            open_app,
        ],
    )

    plan = planner.create_plan(
        objective,
        intent,
    )

    assert (
        objective.status
        == ObjectiveStatus.READY
    )

    assert (
        plan.steps[1].depends_on
        == [plan.steps[0].id]
    )

    assert plan.steps[2].depends_on == []


def test_cyclic_artifact_dependencies_are_rejected():

    registry = FakeToolRegistry(
        {
            "system.a": FakeTool(
                consumes=["b"],
                produces=["a"],
            ),
            "system.b": FakeTool(
                consumes=["a"],
                produces=["b"],
            ),
        }
    )

    planner = Planner(
        tool_resolver=registry.resolve
    )

    objective = make_objective()

    first = Intent(
        action="system.a",
        original_text="ejecutar A",
    )

    second = Intent(
        action="system.b",
        original_text="ejecutar B",
    )

    intent = Intent(
        action=first.action,
        original_text="ejecutar A y B",
        sub_intents=[
            first,
            second,
        ],
    )

    plan = planner.create_plan(
        objective,
        intent,
    )

    assert (
        objective.status
        == ObjectiveStatus.FAILED
    )

    assert "error" in plan.metadata


def test_longer_dependency_graph_is_valid():

    registry = FakeToolRegistry(
        {
            "system.a": FakeTool(
                produces=["a"],
            ),
            "system.b": FakeTool(
                consumes=["a"],
                produces=["b"],
            ),
            "system.c": FakeTool(
                consumes=["b"],
                produces=["c"],
            ),
            "system.d": FakeTool(
                consumes=["c"],
                produces=["d"],
            ),
        }
    )

    planner = Planner(
        tool_resolver=registry.resolve
    )

    objective = make_objective()

    intents = [
        Intent(
            action="system.a",
            original_text="ejecutar A",
        ),
        Intent(
            action="system.b",
            original_text="ejecutar B",
        ),
        Intent(
            action="system.c",
            original_text="ejecutar C",
        ),
        Intent(
            action="system.d",
            original_text="ejecutar D",
        ),
    ]

    intent = Intent(
        action=intents[0].action,
        original_text="A, B, C y D",
        sub_intents=intents,
    )

    plan = planner.create_plan(
        objective,
        intent,
    )

    assert (
        objective.status
        == ObjectiveStatus.READY
    )

    assert (
        plan.steps[1].depends_on
        == [plan.steps[0].id]
    )

    assert (
        plan.steps[2].depends_on
        == [plan.steps[1].id]
    )

    assert (
        plan.steps[3].depends_on
        == [plan.steps[2].id]
    )


def test_cycle_detection_does_not_break_simple_plans():

    registry = FakeToolRegistry(
        {
            "system.open": FakeTool(
                produces=["application_opened"],
            ),
        }
    )

    planner = Planner(
        tool_resolver=registry.resolve
    )

    objective = make_objective()

    intent = Intent(
        action="system.open",
        original_text="abrir aplicación",
    )

    plan = planner.create_plan(
        objective,
        intent,
    )

    assert (
        objective.status
        == ObjectiveStatus.READY
    )

    assert (
        plan.steps[0].depends_on
        == []
    )


def run_tests():

    tests = [
        test_linear_dependency_chain_is_valid,
        test_dependency_graph_can_branch,
        test_independent_steps_can_coexist_with_dependency_graph,
        test_cyclic_artifact_dependencies_are_rejected,
        test_longer_dependency_graph_is_valid,
        test_cycle_detection_does_not_break_simple_plans,
    ]

    passed = 0
    failed = 0

    for test in tests:

        try:

            test()

            print(
                f"PASS: {test.__name__}"
            )

            passed += 1

        except Exception as exc:

            print(
                f"FAIL: {test.__name__}"
            )

            print(
                f"      {type(exc).__name__}: {exc}"
            )

            failed += 1

    print()

    print(
        "COGNITIVE PLANNING 6.3: "
        f"{passed}/{len(tests)} PASSED"
    )

    if failed:
        raise SystemExit(1)


if __name__ == "__main__":
    run_tests()
