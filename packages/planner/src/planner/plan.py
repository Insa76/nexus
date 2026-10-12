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

    Un paso puede declarar:

    - depends_on: pasos que deben completarse antes
    - consumes: artifacts que necesita como entrada
    - produces: artifacts que genera como salida

    Estas relaciones forman el contrato de ejecución
    del paso.
    """

    id: str

    name: str

    description: str

    action: str

    status: StepStatus = StepStatus.PENDING

    metadata: dict = Field(
        default_factory=dict
    )

    depends_on: list[str] = Field(
        default_factory=list
    )

    consumes: list[str] = Field(
        default_factory=list
    )

    produces: list[str] = Field(
        default_factory=list
    )


class ExecutionPlan(BaseModel):
    """
    Plan generado para cumplir un Objective.

    Los pasos forman una estructura de ejecución
    basada en dependencias.
    """

    objective_id: str

    steps: list[PlanStep] = Field(
        default_factory=list
    )

    current_step: int = 0

    completed: bool = False

    metadata: dict = Field(
        default_factory=dict
    )
