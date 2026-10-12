from __future__ import annotations

from collections.abc import Callable, Mapping, Sequence
from typing import Any

from context.models import AssistantContext
from memory import WorkingMemory
from memory.semantic_retriever import SemanticRetriever


ContextProvider = Callable[
    [str | None, AssistantContext | None],
    Mapping[str, Any] | None,
]


class ContextBuilder:
    """
    Construye el contexto cognitivo que NEXUS entrega
    al sistema de interpretación.

    El contexto se divide en:

    - recent_interactions
    - recent_episodes
    - last_request
    - last_intent
    - last_result
    - references
    - semantic_knowledge

    Regla fundamental:

    El contexto puede utilizar intenciones para comprender
    lo que el usuario quiso hacer, pero el estado ejecutado
    del sistema debe derivarse de resultados de ejecución
    exitosos.

    Una intención no constituye por sí misma evidencia de
    que una acción haya ocurrido.

    El conocimiento semántico es conocimiento reutilizable.
    No constituye autoridad sobre el estado real del sistema.
    """

    _CONTEXT_ENTRY_TYPES = {
        "user_request",
        "intent",
        "objective",
        "plan",
        "plan_final",
        "execution_result",
        "error",
    }

    _EPISODE_ENTRY_TYPE = "episode"

    def __init__(
        self,
        max_entries: int = 50,
        max_episodes: int = 10,
        semantic_retriever: SemanticRetriever | None = None,
        max_semantic_results: int = 10,
        assistant_context: AssistantContext | None = None,
        context_providers: Sequence[ContextProvider] = (),
    ) -> None:
        self._max_entries = max_entries
        self._max_episodes = max_episodes
        self._semantic_retriever = semantic_retriever
        self._max_semantic_results = max_semantic_results
        self._assistant_context = assistant_context
        self._context_providers = tuple(context_providers)

    def build(
        self,
        memory: WorkingMemory,
        semantic_query: str | None = None,
    ) -> dict[str, Any]:
        entries = memory.recent(
            self._max_entries
        )

        episode_entries = memory.find(
            self._EPISODE_ENTRY_TYPE
        )

        episode_entries = episode_entries[
            -self._max_episodes:
        ]

        context: dict[str, Any] = {
            "recent_interactions": [],
            "recent_episodes": [],
            "last_request": None,
            "last_intent": None,
            "last_result": None,
            "references": {
                "last_action": None,
                "last_application": None,
                "last_executed_application": None,
                "last_volume": None,
                "previous_volume": None,
                "last_capture_available": False,
            },
            "semantic_knowledge": [],
        }

        for entry in entries:
            if entry.type not in self._CONTEXT_ENTRY_TYPES:
                continue

            item = {
                "type": entry.type,
                "data": entry.data,
            }

            context["recent_interactions"].append(
                item
            )

            if entry.type == "user_request":
                context["last_request"] = (
                    entry.data
                )

            elif entry.type == "intent":
                context["last_intent"] = (
                    entry.data
                )

            elif entry.type == "execution_result":
                context["last_result"] = (
                    entry.data
                )

        for entry in episode_entries:
            context["recent_episodes"].append(
                entry.data
            )

        context["references"] = (
            self._build_references(context)
        )

        context["semantic_knowledge"] = (
            self._build_semantic_knowledge(
                semantic_query
            )
        )

        for provider in self._context_providers:
            provided_context = provider(
                semantic_query,
                self._assistant_context,
            )

            if provided_context is None:
                continue

            for key, value in provided_context.items():
                context[key] = value

        return context

    def _build_semantic_knowledge(
        self,
        semantic_query: str | None,
    ) -> list[dict[str, Any]]:
        """
        Recupera conocimiento semántico relevante.

        Esta información es contextual y no autoritativa.
        Nunca reemplaza el estado obtenido mediante ejecución.
        """

        if self._semantic_retriever is None:
            return []

        if not isinstance(
            semantic_query,
            str,
        ):
            return []

        semantic_query = semantic_query.strip()

        if not semantic_query:
            return []

        matches = self._semantic_retriever.search(
            semantic_query,
            limit=self._max_semantic_results,
        )

        knowledge: list[dict[str, Any]] = []

        for match in matches:
            fact = match.fact

            knowledge.append(
                {
                    "subject": fact.subject,
                    "predicate": fact.predicate,
                    "value": fact.value,
                    "confidence": fact.confidence,
                    "source": fact.source,
                    "score": match.score,
                }
            )

        return knowledge

    def _build_references(
        self,
        context: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Construye referencias reutilizables a partir
        de las interacciones recientes.

        Las referencias son derivadas, no autoritativas.

        Las intenciones indican intención del usuario.

        Los resultados de ejecución exitosos indican
        que una acción realmente ocurrió.

        Por lo tanto:

            intent != estado ejecutado

        El estado ejecutado tiene prioridad.
        """

        references: dict[str, Any] = {
            "last_action": None,
            "last_application": None,
            "last_executed_application": None,
            "last_volume": None,
            "previous_volume": None,
            "last_capture_available": False,
        }

        recent_interactions = context.get(
            "recent_interactions",
            [],
        )

        if not isinstance(
            recent_interactions,
            list,
        ):
            return references

        #
        # ---------------------------------------------------------
        # Última acción realmente ejecutada
        # ---------------------------------------------------------
        #

        successful_execution_actions: list[str] = []

        for index in range(
            len(recent_interactions)
        ):
            interaction = recent_interactions[index]

            if not isinstance(
                interaction,
                dict,
            ):
                continue

            if interaction.get("type") != "execution_result":
                continue

            data = interaction.get(
                "data",
                {},
            )

            if not isinstance(
                data,
                dict,
            ):
                continue

            if data.get("success") is not True:
                continue

            action = self._find_associated_intent(
                recent_interactions,
                index,
            )

            if action:
                successful_execution_actions.append(
                    action
                )

        if successful_execution_actions:
            references["last_action"] = (
                successful_execution_actions[-1]
            )

        #
        # ---------------------------------------------------------
        # Estado ejecutado de aplicaciones
        # ---------------------------------------------------------
        #

        for index in range(
            len(recent_interactions) - 1,
            -1,
            -1,
        ):
            interaction = recent_interactions[index]

            if not isinstance(
                interaction,
                dict,
            ):
                continue

            if interaction.get("type") != "execution_result":
                continue

            data = interaction.get(
                "data",
                {},
            )

            if not isinstance(
                data,
                dict,
            ):
                continue

            if data.get("success") is not True:
                continue

            action = self._find_associated_intent(
                recent_interactions,
                index,
            )

            output = data.get(
                "output",
                {},
            )

            if not isinstance(
                output,
                dict,
            ):
                output = {}

            if action == "system.open_app":
                status = output.get(
                    "status"
                )

                application = output.get(
                    "application"
                )

                if (
                    status == "opened"
                    and isinstance(
                        application,
                        str,
                    )
                    and application.strip()
                ):
                    references[
                        "last_application"
                    ] = application.strip()

                    references[
                        "last_executed_application"
                    ] = application.strip()

                    break

            if action == "system.close_app":
                status = output.get(
                    "status"
                )

                application = output.get(
                    "application"
                )

                if (
                    status == "closed"
                    and isinstance(
                        application,
                        str,
                    )
                    and application.strip()
                ):
                    references[
                        "last_application"
                    ] = application.strip()

                    references[
                        "last_executed_application"
                    ] = None

                    break

        #
        # ---------------------------------------------------------
        # Estado ejecutado del volumen
        # ---------------------------------------------------------
        #

        volume_values: list[float] = []

        for index in range(
            len(recent_interactions) - 1,
            -1,
            -1,
        ):
            interaction = recent_interactions[index]

            if not isinstance(
                interaction,
                dict,
            ):
                continue

            if interaction.get("type") != "execution_result":
                continue

            data = interaction.get(
                "data",
                {},
            )

            if not isinstance(
                data,
                dict,
            ):
                continue

            if data.get("success") is not True:
                continue

            action = self._find_associated_intent(
                recent_interactions,
                index,
            )

            output = data.get(
                "output",
                {},
            )

            if not isinstance(
                output,
                dict,
            ):
                continue

            if action not in {
                "system.set_volume",
                "system.get_volume",
            }:
                continue

            volume = output.get(
                "volume"
            )

            try:
                volume = float(volume)
            except (
                TypeError,
                ValueError,
            ):
                continue

            volume_values.append(
                volume
            )

        if volume_values:
            references["last_volume"] = (
                volume_values[0]
            )

        if len(volume_values) > 1:
            references["previous_volume"] = (
                volume_values[1]
            )

        #
        # ---------------------------------------------------------
        # Última captura realmente disponible
        # ---------------------------------------------------------
        #

        for index in range(
            len(recent_interactions) - 1,
            -1,
            -1,
        ):
            interaction = recent_interactions[index]

            if not isinstance(
                interaction,
                dict,
            ):
                continue

            if interaction.get("type") != "execution_result":
                continue

            data = interaction.get(
                "data",
                {},
            )

            if not isinstance(
                data,
                dict,
            ):
                continue

            if data.get("success") is not True:
                continue

            action = self._find_associated_intent(
                recent_interactions,
                index,
            )

            if action != "system.screen_capture":
                continue

            artifacts = data.get(
                "artifacts",
                {},
            )

            if (
                isinstance(
                    artifacts,
                    dict,
                )
                and "image" in artifacts
            ):
                references[
                    "last_capture_available"
                ] = True
                break

        #
        # ---------------------------------------------------------
        # Fallback episódico
        # ---------------------------------------------------------
        #

        if not references[
            "last_capture_available"
        ]:
            for episode in reversed(
                context.get(
                    "recent_episodes",
                    [],
                )
            ):
                if not isinstance(
                    episode,
                    dict,
                ):
                    continue

                if (
                    episode.get("action")
                    == "system.screen_capture"
                    and episode.get("success") is True
                ):
                    references[
                        "last_capture_available"
                    ] = True
                    break

        return references

    def _find_associated_intent(
        self,
        interactions: list[dict[str, Any]],
        execution_index: int,
    ) -> str | None:
        """
        Busca hacia atrás la intención asociada al resultado
        de ejecución.

        La estructura actual de WorkingMemory registra:

            user_request
            intent
            objective
            plan
            plan_final
            execution_result

        Por lo tanto, el intent más cercano anterior al
        execution_result representa la acción que produjo
        dicho resultado.
        """

        for index in range(
            execution_index - 1,
            -1,
            -1,
        ):
            interaction = interactions[index]

            if not isinstance(
                interaction,
                dict,
            ):
                continue

            if interaction.get("type") != "intent":
                continue

            data = interaction.get(
                "data",
                {},
            )

            if not isinstance(
                data,
                dict,
            ):
                continue

            action = data.get(
                "action"
            )

            if isinstance(
                action,
                str,
            ):
                return action

        return None
