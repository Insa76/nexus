from __future__ import annotations

import pytest

from actions.base import Action
from actions.manager import ActionManager
from actions.registry import ActionRegistry

from planner.execution_context import ExecutionContext
from planner.objective import Objective, ObjectiveStatus
from planner.plan import ExecutionPlan, PlanStep, StepStatus

from security import (
    ActionAuthorization,
    ActionPolicy,
    ActionPolicyStore,
    Actor,
    ActorRoleAssignment,
    AssignmentStore,
    AuthorizationService,
    Permission,
    PermissionAction,
    Role,
)


ACTION_NAME = "test.protected_action"


class CountingAction(Action):
    name = ACTION_NAME
    description = "Action used to test authorization."

    def __init__(self) -> None:
        self.called = False

    async def execute(self, context, step) -> None:
        self.called = True
        context.add_result("executed", True)


def build_authorization(
    *,
    assigned: bool,
    register_policy: bool = True,
) -> tuple[ActionAuthorization, Actor]:

    actor = Actor.user("user-1")

    permission = Permission(
        resource=ACTION_NAME,
        action=PermissionAction.EXECUTE,
    )

    assignments = AssignmentStore()

    if assigned:
        role = Role(
            id="operator",
            name="Operator",
            permissions=frozenset({permission}),
        )

        assignments.add(
            ActorRoleAssignment(
                actor=actor,
                role=role,
            )
        )

    policy_store = ActionPolicyStore()

    if register_policy:
        policy_store.register(
            ActionPolicy(
                action_name=ACTION_NAME,
                permission=permission,
            )
        )

    authorization = ActionAuthorization(
        policy_store=policy_store,
        authorization=AuthorizationService(assignments),
    )

    return authorization, actor


def build_context(
    actor: Actor | None,
) -> ExecutionContext:

    objective = Objective(
        id="objective-1",
        title="Test authorization",
        status=ObjectiveStatus.RUNNING,
        priority=1,
        metadata={},
    )

    step = PlanStep(
        id="step-1",
        name="Protected action",
        description="Authorization test",
        action=ACTION_NAME,
    )

    plan = ExecutionPlan(
        objective_id=objective.id,
        steps=[step],
    )

    return ExecutionContext(
        objective=objective,
        plan=plan,
        actor_id=actor.id if actor else None,
        actor_type=(
            actor.actor_type.value if actor else None
        ),
    )


@pytest.mark.asyncio
async def test_authorized_action_executes() -> None:
    authorization, actor = build_authorization(
        assigned=True,
    )

    action = CountingAction()
    registry = ActionRegistry()
    registry.register(action)

    manager = ActionManager(
        registry,
        action_authorization=authorization,
    )

    context = build_context(actor)

    await manager.execute(context)

    assert action.called is True
    assert context.results["executed"] is True
    assert context.plan.steps[0].status == StepStatus.COMPLETED
    assert context.step_evidence["step-1"]["status"] == "completed"


@pytest.mark.asyncio
async def test_denied_action_is_not_executed() -> None:
    authorization, actor = build_authorization(
        assigned=False,
    )

    action = CountingAction()
    registry = ActionRegistry()
    registry.register(action)

    manager = ActionManager(
        registry,
        action_authorization=authorization,
    )

    context = build_context(actor)

    await manager.execute(context)

    assert action.called is False
    assert context.plan.steps[0].status == StepStatus.FAILED
    assert context.objective.status == ObjectiveStatus.FAILED
    assert context.finished is True
    assert context.plan.completed is False
    assert context.has_errors() is True
    assert context.step_evidence["step-1"]["status"] == "failed"
    assert context.step_evidence["step-1"]["authorization"]["allowed"] is False


@pytest.mark.asyncio
async def test_missing_actor_is_denied() -> None:
    authorization, _ = build_authorization(
        assigned=True,
    )

    action = CountingAction()
    registry = ActionRegistry()
    registry.register(action)

    manager = ActionManager(
        registry,
        action_authorization=authorization,
    )

    context = build_context(None)

    await manager.execute(context)

    assert action.called is False
    assert context.plan.steps[0].status == StepStatus.FAILED
    assert context.finished is True
    assert context.has_errors() is True


@pytest.mark.asyncio
async def test_missing_policy_is_denied() -> None:
    authorization, actor = build_authorization(
        assigned=True,
        register_policy=False,
    )

    action = CountingAction()
    registry = ActionRegistry()
    registry.register(action)

    manager = ActionManager(
        registry,
        action_authorization=authorization,
    )

    context = build_context(actor)

    await manager.execute(context)

    assert action.called is False
    assert context.plan.steps[0].status == StepStatus.FAILED
    assert context.finished is True
    assert context.has_errors() is True
