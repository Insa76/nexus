from __future__ import annotations

from planner.plan import PlanStep
from planner.execution_context import ExecutionContext

from actions.base import Action

from memory.episode_memory import EpisodeMemory


class GetPreviousEpisodeAction(Action):
    """
    Action para consultar el episodio inmediatamente
    anterior al último episodio registrado.

    No interpreta intenciones.
    No ejecuta acciones del sistema.
    No genera lenguaje natural.

    Devuelve únicamente el episodio estructurado.
    """

    name = "system.get_previous_episode"

    description = (
        "Consulta la acción realizada inmediatamente "
        "antes de la última acción de NEXUS."
    )

    parameters = {}

    internal = True

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

        episode = self._episode_memory.previous()

        if episode is None:

            context.add_result(
                "found",
                False,
            )

            context.add_result(
                "episode",
                None,
            )

            context.add_result(
                "status",
                "read",
            )

            context.add_result(
                "mode",
                "previous",
            )

            return

        context.add_result(
            "found",
            True,
        )

        context.add_result(
            "episode",
            episode.model_dump(),
        )

        context.add_result(
            "status",
            "read",
        )

        context.add_result(
            "mode",
            "previous",
        )
