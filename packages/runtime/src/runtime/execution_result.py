from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class ExecutionResult(BaseModel):
    """
    Resultado final de la ejecución de un Objective.
    """

    success: bool = True

    message: str = ""

    output: Any = None

    artifacts: dict[str, Any] = Field(default_factory=dict)

    metadata: dict[str, Any] = Field(default_factory=dict)

    execution_time: float = 0.0