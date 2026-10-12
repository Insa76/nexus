from __future__ import annotations

from planner.plan import PlanStep
from planner.execution_context import ExecutionContext

from actions.base import Action

from memory.episode_memory import EpisodeMemory


class GetLastEpisodeAction(Action):
    """
    Action para consultar el último episodio
    registrado por NEXUS.

    No interpreta intenciones.
    No ejecuta acciones del sistema.
    No genera lenguaje natural.

    Devuelve únicamente el episodio estructurado.
    """

    name = "system.get_last_episode"

    description = (
        "Consulta la última acción realizada "
        "por NEXUS."
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

        episode = (
            self._episode_memory.last()
        )

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
            "last",
        )
