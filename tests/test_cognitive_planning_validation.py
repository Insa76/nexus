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


def test_consumer_without_producer_is_detected():

    registry = FakeToolRegistry(
        {
            "system.inspect": FakeTool(
                consumes=["image"],
            ),
        }
    )

    planner = Planner(
        tool_resolver=registry.resolve
    )

    objective = make_objective()

    intent = Intent(
        action="system.inspect",
        original_text="inspeccionar imagen",
    )

    plan = planner.create_plan(
        objective,
        intent,
    )

    assert len(plan.steps) == 1

    assert plan.steps[0].consumes == [
        "image"
    ]

    assert (
        objective.status
        == ObjectiveStatus.FAILED
    )


def test_missing_artifact_is_reported_in_plan_metadata():

    registry = FakeToolRegistry(
        {
            "system.inspect": FakeTool(
                consumes=["image"],
            ),
        }
    )

    planner = Planner(
        tool_resolver=registry.resolve
    )

    objective = make_objective()

    intent = Intent(
        action="system.inspect",
        original_text="inspeccionar imagen",
    )

    plan = planner.create_plan(
        objective,
        intent,
    )

    assert "error" in plan.metadata


def test_existing_producer_makes_plan_valid():

    registry = FakeToolRegistry(
        {
            "system.capture": FakeTool(
                produces=["image"],
            ),
            "system.inspect": FakeTool(
                consumes=["image"],
            ),
        }
    )

    planner = Planner(
        tool_resolver=registry.resolve
    )

    objective = make_objective()

    capture = Intent(
        action="system.capture",
        original_text="capturar pantalla",
    )

    inspect_capture = Intent(
        action="system.inspect",
        original_text="inspeccionar captura",
    )

    intent = Intent(
        action=capture.action,
        original_text=(
            "capturar pantalla y "
            "inspeccionar captura"
        ),
        sub_intents=[
            capture,
            inspect_capture,
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

    assert plan.metadata == {}


def test_independent_consumer_is_invalid_without_matching_artifact():

    registry = FakeToolRegistry(
        {
            "system.capture": FakeTool(
                produces=["image"],
            ),
            "system.use_document": FakeTool(
                consumes=["document"],
            ),
        }
    )

    planner = Planner(
        tool_resolver=registry.resolve
    )

    objective = make_objective()

    capture = Intent(
        action="system.capture",
        original_text="capturar pantalla",
    )

    use_document = Intent(
        action="system.use_document",
        original_text="usar documento",
    )

    intent = Intent(
        action=capture.action,
        original_text=(
            "capturar pantalla y "
            "usar documento"
        ),
        sub_intents=[
            capture,
            use_document,
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


def test_multiple_producers_are_not_silently_ambiguous():

    registry = FakeToolRegistry(
        {
            "system.capture_a": FakeTool(
                produces=["image"],
            ),
            "system.capture_b": FakeTool(
                produces=["image"],
            ),
            "system.inspect": FakeTool(
                consumes=["image"],
            ),
        }
    )

    planner = Planner(
        tool_resolver=registry.resolve
    )

    objective = make_objective()

    first = Intent(
        action="system.capture_a",
        original_text="capturar pantalla A",
    )

    second = Intent(
        action="system.capture_b",
        original_text="capturar pantalla B",
    )

    consumer = Intent(
        action="system.inspect",
        original_text="inspeccionar captura",
    )

    intent = Intent(
        action=first.action,
        original_text=(
            "capturar A, capturar B "
            "y luego inspeccionar"
        ),
        sub_intents=[
            first,
            second,
            consumer,
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


def test_valid_plan_has_no_structural_error():

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
        original_text="capturar pantalla",
    )

    inspect_capture = Intent(
        action="system.inspect",
        original_text="inspeccionar captura",
    )

    process = Intent(
        action="system.process",
        original_text="procesar inspección",
    )

    intent = Intent(
        action=capture.action,
        original_text=(
            "capturar, inspeccionar "
            "y procesar"
        ),
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

    assert plan.metadata == {}

    assert (
        plan.steps[1].depends_on
        == [plan.steps[0].id]
    )

    assert (
        plan.steps[2].depends_on
        == [plan.steps[1].id]
    )


def run_tests():

    tests = [
        test_consumer_without_producer_is_detected,
        test_missing_artifact_is_reported_in_plan_metadata,
        test_existing_producer_makes_plan_valid,
        test_independent_consumer_is_invalid_without_matching_artifact,
        test_multiple_producers_are_not_silently_ambiguous,
        test_valid_plan_has_no_structural_error,
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
        "COGNITIVE PLANNING 6.2: "
        f"{passed}/{len(tests)} PASSED"
    )

    if failed:
        raise SystemExit(1)


if __name__ == "__main__":
    run_tests()
