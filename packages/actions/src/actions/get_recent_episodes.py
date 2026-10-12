from __future__ import annotations

from planner.plan import PlanStep
from planner.execution_context import ExecutionContext

from actions.base import Action

from memory.episode_memory import EpisodeMemory


class GetRecentEpisodesAction(Action):
    """
    Action para consultar la memoria episódica reciente
    de NEXUS.

    No interpreta intenciones.
    No ejecuta acciones del sistema.
    No genera lenguaje natural.

    Devuelve únicamente episodios estructurados.
    """

    name = "system.get_recent_episodes"

    description = (
        "Consulta las acciones realizadas "
        "recientemente por NEXUS."
    )

    parameters = {
        "limit": {
            "type": "integer",
            "required": False,
            "description": (
                "Cantidad de episodios recientes "
                "a devolver."
            ),
        },
    }

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

        limit = step.metadata.get(
            "limit",
            5,
        )

        #
        # Validar limit
        #

        if isinstance(
            limit,
            bool,
        ):

            context.add_error(
                "Episode limit must be an integer."
            )

            return

        try:

            limit = int(limit)

        except (
            TypeError,
            ValueError,
        ):

            context.add_error(
                "Episode limit must be an integer."
            )

            return

        #
        # Rango razonable
        #

        if limit <= 0:

            context.add_error(
                "Episode limit must be greater than zero."
            )

            return

        #
        # Evitamos consultas excesivamente grandes.
        #

        limit = min(
            limit,
            20,
        )

        #
        # Obtener episodios
        #

        episodes = (
            self._episode_memory.recent(
                limit=limit,
            )
        )

        #
        # Convertir a estructuras serializables
        #

        items = [
            episode.model_dump()
            for episode in episodes
        ]

        #
        # Resultado
        #

        context.add_result(
            "episodes",
            items,
        )

        context.add_result(
            "count",
            len(items),
        )

        context.add_result(
            "limit",
            limit,
        )

        context.add_result(
            "status",
            "read",
        )
