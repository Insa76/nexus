from __future__ import annotations

from planner.plan import PlanStep
from planner.execution_context import ExecutionContext

from actions.base import Action

from memory.state_history import StateHistory
from providers.provider_manager import ProviderManager


class RestorePreviousVolumeAction(Action):
    """
    Action para restaurar el volumen anterior
    registrado en el historial de NEXUS.
    """

    name = "system.restore_previous_volume"

    internal = True

    def __init__(
        self,
        provider_manager: ProviderManager,
        state_history: StateHistory,
    ) -> None:

        self._provider_manager = provider_manager
        self._state_history = state_history

    async def execute(
        self,
        context: ExecutionContext,
        step: PlanStep,
    ) -> None:

        #
        # Obtener el volumen anterior
        #

        previous_volume = (
            self._state_history.previous_restorable(
        "volume"
        )
    )

        if previous_volume is None:

            context.add_error(
                "No previous volume state is available."
            )

            return

        #
        # Validar valor
        #

        try:

            previous_volume = float(
                previous_volume
            )

        except (
            TypeError,
            ValueError,
        ):

            context.add_error(
                "Previous volume state is invalid."
            )

            return

        #
        # Validar rango
        #

        if (
            previous_volume < 0
            or previous_volume > 100
        ):

            context.add_error(
                "Previous volume state must be between 0 and 100."
            )

            return

        #
        # Restaurar volumen
        #

        try:

            result = (
                await self._provider_manager.execute(
                    provider="local",
                    tool="windows.set_volume",
                    parameters={
                        "level": previous_volume,
                    },
                )
            )

        except Exception as exc:

            context.add_error(
                f"Failed to restore previous volume: {exc}"
            )

            return

        #
        # Resultado
        #

        context.add_result(
            "volume",
            result,
        )

        context.add_result(
            "status",
            "restored",
        )
