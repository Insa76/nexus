from __future__ import annotations

from collections.abc import Callable, Mapping, Sequence
from typing import Any

from context import AssistantContext

from memory import WorkingMemory
from memory.semantic_retriever import SemanticRetriever


ContextProvider = Callable[
    [str | None, AssistantContext | None],
    Mapping[str, Any] | None,
]


class ContextBuilder:
    """
    Construye contexto cognitivo a partir de:

    - WorkingMemory
    - conocimiento semántico
    - AssistantContext opcional
    - proveedores de contexto externos

    No interpreta la solicitud.
    No ejecuta acciones.
    No modifica memoria.

    Su responsabilidad es seleccionar y organizar
    información relevante para entregársela al
    IntentProvider.

    Los proveedores de contexto permiten incorporar
    información proveniente de capacidades cognitivas
    externas sin acoplar este componente a un
    subsistema concreto.
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
        max_semantic_matches: int = 10,
        assistant_context: AssistantContext | None = None,
        context_providers: Sequence[ContextProvider] = (),
    ) -> None:
        self._max_entries = max_entries
        self._max_episodes = max_episodes
        self._semantic_retriever = semantic_retriever
        self._max_semantic_matches = max_semantic_matches
        self._assistant_context = assistant_context
        self._context_providers = tuple(
            context_providers
        )

    def set_assistant_context(
        self,
        assistant_context: AssistantContext | None,
    ) -> None:
        """Actualiza el contexto configurado por defecto."""
        if (
            assistant_context is not None
            and not isinstance(assistant_context, AssistantContext)
        ):
            raise TypeError(
                "assistant_context debe ser AssistantContext o None."
            )
        self._assistant_context = assistant_context

    def build(
        self,
        memory: WorkingMemory,
        semantic_query: str | None = None,
        assistant_context: AssistantContext | None = None,
    ) -> dict[str, Any]:
        """
        Construye un contexto estructurado a partir
        de las entradas relevantes de memoria.

        Si existe un SemanticRetriever y se proporciona
        una consulta, incorpora conocimiento semántico
        relevante sin modificar la memoria.

        Si existe un AssistantContext, incorpora el
        contexto del usuario, organización y proyectos.

        El AssistantContext recibido en build() tiene
        prioridad sobre el configurado en el constructor.

        Los context providers reciben la consulta
        actual y el AssistantContext efectivo y pueden
        aportar información adicional al contexto
        cognitivo.

        Los providers no modifican el contexto
        directamente: devuelven datos que el builder
        incorpora al resultado final.
        """

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
            "semantic_knowledge": [],
            "assistant_context": None,
            "last_request": None,
            "last_intent": None,
            "last_result": None,
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
                context["last_request"] = entry.data

            elif entry.type == "intent":
                context["last_intent"] = entry.data

            elif entry.type == "execution_result":
                context["last_result"] = entry.data

        for entry in episode_entries:
            context["recent_episodes"].append(
                entry.data
            )

        effective_assistant_context = (
            assistant_context
            if assistant_context is not None
            else self._assistant_context
        )

        if effective_assistant_context is not None:
            context["assistant_context"] = (
                effective_assistant_context.to_dict()
            )

        context["semantic_knowledge"] = (
            self._build_semantic_knowledge(
                semantic_query
            )
        )

        #
        # Context Providers
        #

        for provider in self._context_providers:
            provided_context = provider(
                semantic_query,
                effective_assistant_context,
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
        Recupera conocimiento semántico relevante
        para la consulta actual.

        La recuperación se realiza en dos niveles:

        1. consulta completa;
        2. términos individuales de la consulta.

        Esto permite que una solicitud como
        "Cerrá Chrome" encuentre un hecho cuyo sujeto
        sea "chrome", sin modificar la lógica del
        SemanticRetriever.

        No se realiza interpretación semántica compleja.
        """

        if (
            self._semantic_retriever is None
            or not semantic_query
            or not semantic_query.strip()
        ):
            return []

        matches_by_key: dict[
            tuple[str, str],
            dict[str, Any],
        ] = {}

        #
        # 1. Consulta completa
        #

        matches = self._semantic_retriever.search(
            semantic_query,
            limit=self._max_semantic_matches,
        )

        self._add_semantic_matches(
            matches_by_key,
            matches,
        )

        #
        # 2. Términos individuales
        #

        terms = self._semantic_terms(
            semantic_query
        )

        for term in terms:
            matches = self._semantic_retriever.search(
                term,
                limit=self._max_semantic_matches,
            )

            self._add_semantic_matches(
                matches_by_key,
                matches,
            )

        knowledge = list(
            matches_by_key.values()
        )

        knowledge.sort(
            key=lambda item: (
                -float(item["score"]),
                -float(item["confidence"]),
                item["subject"],
                item["predicate"],
            )
        )

        return knowledge[
            :self._max_semantic_matches
        ]

    @staticmethod
    def _add_semantic_matches(
        destination: dict[
            tuple[str, str],
            dict[str, Any],
        ],
        matches: list[Any],
    ) -> None:
        """
        Convierte SemanticMatch en datos simples
        para el contexto cognitivo.

        Los duplicados se consolidan por
        subject + predicate.
        """

        for match in matches:
            fact = match.fact

            key = (
                fact.subject,
                fact.predicate,
            )

            item = {
                "subject": fact.subject,
                "predicate": fact.predicate,
                "value": fact.value,
                "confidence": fact.confidence,
                "source": fact.source,
                "metadata": dict(
                    fact.metadata
                ),
                "score": match.score,
            }

            existing = destination.get(key)

            if existing is None:
                destination[key] = item
                continue

            #
            # Conservamos la mejor puntuación obtenida
            # para el mismo hecho.
            #

            if item["score"] > existing["score"]:
                destination[key] = item

    @staticmethod
    def _semantic_terms(
        query: str,
    ) -> list[str]:
        """
        Obtiene términos simples de una consulta.

        No realiza NLP ni interpretación.
        Solamente normaliza espacios y elimina
        signos básicos de puntuación.

        Los términos de una sola letra se descartan.
        """

        normalized = query.strip().lower()

        for character in (
            "¿",
            "?",
            "¡",
            "!",
            ".",
            ",",
            ";",
            ":",
            "(",
            ")",
            "[",
            "]",
            "{",
            "}",
            '"',
            "'",
        ):
            normalized = normalized.replace(
                character,
                " ",
            )

        terms: list[str] = []
        seen: set[str] = set()

        for term in normalized.split():
            if len(term) < 2:
                continue

            if term in seen:
                continue

            seen.add(term)
            terms.append(term)

        return terms
