from __future__ import annotations

from planner.intent import Intent
from planner.objective import (
    Objective,
    ObjectiveStatus,
)
from planner.plan import (
    StepStatus,
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


def test_simple_plan_remains_compatible():

    registry = FakeToolRegistry(
        {
            "system.open_app": FakeTool(
                produces=["application_opened"]
            )
        }
    )

    planner = Planner(
        tool_resolver=registry.resolve
    )

    objective = make_objective()

    intent = Intent(
        action="system.open_app",
        original_text="abrir chrome",
        parameters={
            "application": "chrome",
        },
    )

    plan = planner.create_plan(
        objective,
        intent,
    )

    assert len(plan.steps) == 1
    assert (
        plan.steps[0].action
        == "system.open_app"
    )
    assert (
        plan.steps[0].depends_on
        == []
    )
    assert (
        objective.status
        == ObjectiveStatus.READY
    )


def test_compound_plan_creates_dependency_when_producer_comes_first():

    registry = FakeToolRegistry(
        {
            "system.capture": FakeTool(
                produces=["image"]
            ),
            "system.inspect": FakeTool(
                consumes=["image"],
                produces=["inspection"],
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

    assert len(plan.steps) == 2

    producer = plan.steps[0]
    consumer = plan.steps[1]

    assert producer.id not in []
    assert (
    producer.id
    in consumer.depends_on
)


def test_compound_plan_creates_dependency_when_producer_comes_later():

    registry = FakeToolRegistry(
        {
            "system.inspect": FakeTool(
                consumes=["image"],
                produces=["inspection"],
            ),
            "system.capture": FakeTool(
                produces=["image"]
            ),
        }
    )

    planner = Planner(
        tool_resolver=registry.resolve
    )

    objective = make_objective()

    inspect_capture = Intent(
        action="system.inspect",
        original_text="inspeccionar captura",
    )

    capture = Intent(
        action="system.capture",
        original_text="capturar pantalla",
    )

    intent = Intent(
        action=inspect_capture.action,
        original_text=(
            "inspeccionar captura y "
            "capturar pantalla"
        ),
        sub_intents=[
            inspect_capture,
            capture,
        ],
    )

    plan = planner.create_plan(
        objective,
        intent,
    )

    assert len(plan.steps) == 2

    consumer = plan.steps[0]
    producer = plan.steps[1]

    assert (
        producer.id
        in consumer.depends_on
    )


def test_independent_steps_do_not_get_dependencies():

    registry = FakeToolRegistry(
        {
            "system.capture": FakeTool(
                produces=["image"]
            ),
            "system.open": FakeTool(
                produces=["application_opened"]
            ),
        }
    )

    planner = Planner(
        tool_resolver=registry.resolve
    )

    objective = make_objective()

    first = Intent(
        action="system.capture",
        original_text="capturar pantalla",
    )

    second = Intent(
        action="system.open",
        original_text="abrir chrome",
        parameters={
            "application": "chrome",
        },
    )

    intent = Intent(
        action=first.action,
        original_text=(
            "capturar pantalla y "
            "abrir chrome"
        ),
        sub_intents=[
            first,
            second,
        ],
    )

    plan = planner.create_plan(
        objective,
        intent,
    )

    assert len(plan.steps) == 2

    assert plan.steps[0].depends_on == []
    assert plan.steps[1].depends_on == []


def test_dependency_is_based_on_artifact_not_step_position():

    registry = FakeToolRegistry(
        {
            "system.produce": FakeTool(
                produces=["shared"]
            ),
            "system.consume": FakeTool(
                consumes=["shared"]
            ),
        }
    )

    planner = Planner(
        tool_resolver=registry.resolve
    )

    objective = make_objective()

    producer = Intent(
        action="system.produce",
        original_text="producir dato",
    )

    consumer = Intent(
        action="system.consume",
        original_text="usar dato",
    )

    intent = Intent(
        action=producer.action,
        original_text=(
            "producir dato y usar dato"
        ),
        sub_intents=[
            producer,
            consumer,
        ],
    )

    plan = planner.create_plan(
        objective,
        intent,
    )

    assert (
        plan.steps[1].depends_on
        == [plan.steps[0].id]
    )


def test_plan_preserves_step_status_as_pending():

    registry = FakeToolRegistry(
        {
            "system.capture": FakeTool(
                produces=["image"]
            )
        }
    )

    planner = Planner(
        tool_resolver=registry.resolve
    )

    objective = make_objective()

    intent = Intent(
        action="system.capture",
        original_text="capturar pantalla",
    )

    plan = planner.create_plan(
        objective,
        intent,
    )

    assert (
        plan.steps[0].status
        == StepStatus.PENDING
    )

    assert (
        plan.completed is False
    )


def run_tests():

    tests = [
        test_simple_plan_remains_compatible,
        test_compound_plan_creates_dependency_when_producer_comes_first,
        test_compound_plan_creates_dependency_when_producer_comes_later,
        test_independent_steps_do_not_get_dependencies,
        test_dependency_is_based_on_artifact_not_step_position,
        test_plan_preserves_step_status_as_pending,
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
        "COGNITIVE PLANNING 6.1: "
        f"{passed}/{len(tests)} PASSED"
    )

    if failed:
        raise SystemExit(1)


if __name__ == "__main__":
    run_tests()
