from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, Field


class StepStatus(str, Enum):
    """
    Estado de un paso del plan.
    """

    PENDING = "pending"
    READY = "ready"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


class PlanStep(BaseModel):
    """
    Representa un paso del plan.
    """

    id: str

    name: str

    description: str

    action: str

    status: StepStatus = StepStatus.PENDING

    metadata: dict = Field(default_factory=dict)


class ExecutionPlan(BaseModel):
    """
    Plan generado para cumplir un Objective.
    """

    objective_id: str

    steps: list[PlanStep] = Field(default_factory=list)

    current_step: int = 0

    completed: bool = False

    metadata: dict = Field(default_factory=dict)