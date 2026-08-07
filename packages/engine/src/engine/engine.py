from __future__ import annotations

from planner.execution_context import ExecutionContext
from runtime.execution_result import ExecutionResult
from runtime.runtime import Runtime


class Engine:
    """
    Motor principal de NEXUS.

    El Engine expone una API simple al resto del sistema y
    delega toda la ejecución al Runtime.
    """

    def __init__(
        self,
        runtime: Runtime,
    ) -> None:

        self._runtime = runtime

    async def execute(
        self,
        context: ExecutionContext,
    ) -> ExecutionResult:
        """
        Ejecuta un contexto completo.
        """

        return await self._runtime.execute(
            context
        )