from __future__ import annotations

from planner.plan import PlanStep
from planner.execution_context import ExecutionContext

from actions.base import Action

from memory.state_history import StateHistory


class GetVolumeHistoryAction(Action):
    """
    Action para consultar el historial del volumen.

    No genera lenguaje natural.
    Devuelve únicamente datos estructurados
    para que las capas superiores puedan decidir
    cómo presentar el resultado.
    """

    name = "system.get_volume_history"

    internal = True

    description = (
        "Consulta el historial del volumen."
    )

    parameters = {
        "mode": {
            "type": "string",
            "required": True,
            "description": (
                "Modo de consulta: "
                "previous o find."
            ),
        },
        "value": {
            "type": "number",
            "required": False,
            "description": (
                "Valor de volumen a buscar "
                "cuando el modo es find."
            ),
        },
    }

    def __init__(
        self,
        state_history: StateHistory,
    ) -> None:

        self._state_history = state_history

    async def execute(
        self,
        context: ExecutionContext,
        step: PlanStep,
    ) -> None:

        mode = step.metadata.get(
            "mode"
        )

        #
        # Volumen anterior
        #

        if mode == "previous":

            value = self._state_history.previous(
                "volume"
            )

            context.add_result(
                "found",
                value is not None,
            )

            context.add_result(
                "value",
                value,
            )

            context.add_result(
                "mode",
                "previous",
            )

            return

        #
        # Buscar un valor concreto
        #
        # Ejemplo:
        #
        # ¿Qué dejé en 50%?
        #

        if mode == "find":

            requested_value = step.metadata.get(
                "value"
            )

            events = self._state_history.find_events(
                "volume",
                requested_value,
                status="set",
            )

            context.add_result(
                "found",
                bool(events),
            )

            context.add_result(
                "value",
                requested_value
                if events
                else None,
            )

            context.add_result(
                "mode",
                "find",
            )

            return

        #
        # Modo desconocido
        #

        context.add_error(
            "Unknown volume history mode."
        )
