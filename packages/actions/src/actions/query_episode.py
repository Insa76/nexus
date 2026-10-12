from __future__ import annotations

from typing import Any

from actions.base import Action
from memory.episode_memory import EpisodeMemory
from planner.execution_context import ExecutionContext
from planner.plan import PlanStep


class QueryEpisodeAction(Action):
    """
    Consulta memoria episódica y recupera información
    de un episodio anterior.

    La información puede provenir de:
    - parameters del episodio
    - output producido por la ejecución del episodio

    No ejecuta nuevamente la acción consultada.
    """

    name = "system.query_episode"

    description = (
        "Consulta memoria episódica y recupera "
        "información de un episodio anterior."
    )

    parameters = {
        "action": {
            "type": "string",
            "description": (
                "Acción del episodio que se desea consultar."
            ),
        },
        "field": {
            "type": "string",
            "description": (
                "Campo que se desea recuperar del episodio."
            ),
        },
    }

    internal = True

    produces = [
        "episode_query_result",
    ]

    consumes = []

    def __init__(
        self,
        episode_memory: EpisodeMemory,
    ) -> None:
        self._episode_memory = episode_memory

    async def execute(
        self,
        context: ExecutionContext,
        step: PlanStep,
    ) -> None:
        action = step.metadata.get("action")
        field = step.metadata.get("field")

        if not isinstance(action, str) or not action.strip():
            context.add_error(
                "QueryEpisodeAction requiere "
                "un 'action' válido."
            )
            return

        if not isinstance(field, str) or not field.strip():
            context.add_error(
                "QueryEpisodeAction requiere "
                "un 'field' válido."
            )
            return

        action = action.strip()
        field = field.strip()

        episode = (
            self._episode_memory.find_latest_by_action(
                action
            )
        )

        if episode is None:
            context.add_error(
                f"No se encontró ningún episodio "
                f"para la acción '{action}'."
            )
            return

        parameters = episode.parameters

        if not isinstance(parameters, dict):
            parameters = {}

        #
        # Primero buscamos el campo en los parámetros.
        #
        if field in parameters:
            value = parameters[field]

        else:
            #
            # Algunos datos pertenecen al resultado
            # producido por la acción y no a sus parámetros.
            #
            episode_output = episode.output

            if not isinstance(episode_output, dict):
                context.add_error(
                    f"Field '{field}' was not found "
                    f"in the episode for action "
                    f"'{action}'."
                )
                return

            if field not in episode_output:
                context.add_error(
                    f"Field '{field}' was not found "
                    f"in the episode for action "
                    f"'{action}'."
                )
                return

            value = episode_output[field]

        result: dict[str, Any] = {
            "status": "found",
            "action": action,
            "field": field,
            "value": value,
            "original_text": episode.original_text,
            "timestamp": episode.timestamp,
        }

        context.add_result(
            "episode_query_result",
            result,
        )

        #
        # También exponemos los valores individualmente
        # para que otras capas del Runtime puedan utilizarlos.
        #
        context.add_result(
            "status",
            "found",
        )

        context.add_result(
            "action",
            action,
        )

        context.add_result(
            "field",
            field,
        )

        context.add_result(
            "value",
            value,
        )

        context.add_result(
            "original_text",
            episode.original_text,
        )

        context.add_result(
            "timestamp",
            episode.timestamp,
        )
