
from types import SimpleNamespace

import pytest

from actions.base import Action
from actions.manager import ActionManager
from actions.registry import ActionRegistry
from planner.execution_context import ExecutionContext
from planner.objective import Objective, ObjectiveStatus
from planner.plan import ExecutionPlan, PlanStep, StepStatus
from runtime.executor import Executor
from security import (
    ActionAuthorization,
    ActionPolicy,
    ActionPolicyStore,
    AssignmentStore,
    AuthorizationService,
    Permission,
    PermissionAction,
)


class ProtectedAction(Action):
    name = "test.protected_action"

    def __init__(self):
        self.executions = 0

    async def execute(self, context, step):
        self.executions += 1
        context.add_result("protected_action", "executed")


@pytest.mark.asyncio
async def test_denied_action_stops_execution_plan():
    action = ProtectedAction()

    registry = ActionRegistry()
    registry.register(action)

    policy_store = ActionPolicyStore()
    policy_store.register(
        ActionPolicy(
            action_name=action.name,
            permission=Permission(
                resource=action.name,
                action=PermissionAction.EXECUTE,
            ),
        )
    )

    authorization = ActionAuthorization(
        policy_store=policy_store,
        authorization=AuthorizationService(
            AssignmentStore()
        ),
    )

    manager = ActionManager(
        registry,
        action_authorization=authorization,
    )

    runtime = SimpleNamespace(
        action_manager=manager,
    )
    executor = Executor(runtime)

    objective = Objective(
        id="objective-security-test",
        title="Test de autorización",
        status=ObjectiveStatus.READY,
        priority=1,
        metadata={},
    )

    first_step = PlanStep(
        id="step-protected",
        name="Acción protegida",
        description="Debe ser rechazada",
        action=action.name,
    )

    second_step = PlanStep(
        id="step-after",
        name="Paso posterior",
        description="No debe ejecutarse",
        action=action.name,
    )

    plan = ExecutionPlan(
        objective_id=objective.id,
        steps=[first_step, second_step],
    )

    context = ExecutionContext(
        objective=objective,
        plan=plan,
        actor_id="unassigned-user",
        actor_type="user",
    )

    result = await executor.execute(context)

    assert result.success is False
    assert action.executions == 0

    assert first_step.status == StepStatus.FAILED
    assert second_step.status == StepStatus.PENDING

    assert objective.status == ObjectiveStatus.FAILED
    assert context.finished is True
    assert plan.completed is False

    assert any(
        "Authorization denied" in error
        for error in context.errors
    )

    assert context.step_evidence["step-protected"][
        "authorization"
    ]["allowed"] is False
