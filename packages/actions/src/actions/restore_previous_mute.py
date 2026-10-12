from __future__ import annotations

from planner.plan import PlanStep
from planner.execution_context import ExecutionContext

from actions.base import Action

from memory.state_history import StateHistory
from providers.provider_manager import ProviderManager


class RestorePreviousMuteAction(Action):
    """
    Action para restaurar el estado anterior de mute
    registrado en el historial de NEXUS.
    """

    name = "system.restore_previous_mute"

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
        # Obtener el estado anterior
        #

        previous_muted = (
            self._state_history.previous_restorable(
        "muted"
        )
    )

        if previous_muted is None:

            context.add_error(
                "No previous mute state is available."
            )

            return

        #
        # Validar estado
        #

        if not isinstance(
            previous_muted,
            bool,
        ):

            context.add_error(
                "Previous mute state is invalid."
            )

            return

        #
        # Restaurar estado
        #

        try:

            if previous_muted:

                result = (
                    await self._provider_manager.execute(
                        provider="local",
                        tool="windows.mute",
                        parameters={},
                    )
                )

                status = "muted"

            else:

                result = (
                    await self._provider_manager.execute(
                        provider="local",
                        tool="windows.unmute",
                        parameters={},
                    )
                )

                status = "unmuted"

        except Exception as exc:

            context.add_error(
                f"Failed to restore previous mute state: {exc}"
            )

            return

        #
        # Resultado
        #

        context.add_result(
            "muted",
            previous_muted,
        )

        context.add_result(
            "status",
            "restored",
        )

        context.add_result(
            "result",
            result,
        )
