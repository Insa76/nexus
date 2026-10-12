from __future__ import annotations

from typing import Any

from memory.episode_memory import Episode
from memory.semantic_memory import SemanticFact, SemanticMemory


class SemanticKnowledgeExtractor:
    """
    Extrae conocimiento semántico reutilizable a partir
    de episodios exitosos.

    Esta primera versión es deliberadamente conservadora.

    Responsabilidades:
    - analizar un episodio ya ejecutado
    - determinar si contiene conocimiento estable
    - convertirlo en hechos semánticos
    - almacenar esos hechos en SemanticMemory

    No:
    - ejecuta acciones
    - consulta el sistema operativo
    - interpreta lenguaje natural
    - modifica EpisodeMemory
    - decide el estado real del sistema
    """

    def __init__(
        self,
        semantic_memory: SemanticMemory,
    ) -> None:
        self._semantic_memory = semantic_memory

    def extract(
        self,
        episode: Episode,
    ) -> list[SemanticFact]:
        """
        Extrae y almacena los hechos semánticos
        que puedan derivarse inequívocamente del episodio.
        """

        if not episode.success:
            return []

        facts: list[SemanticFact] = []

        action = episode.action

        if action == "system.open_app":
            fact = self._extract_open_app(episode)

            if fact is not None:
                facts.append(fact)

        elif action == "system.close_app":
            fact = self._extract_close_app(episode)

            if fact is not None:
                facts.append(fact)

        elif action == "system.set_volume":
            fact = self._extract_volume(episode)

            if fact is not None:
                facts.append(fact)

        return facts

    def _extract_open_app(
        self,
        episode: Episode,
    ) -> SemanticFact | None:
        application = self._extract_application(
            episode
        )

        if not application:
            return None

        return self._semantic_memory.learn(
            application,
            "es una aplicación",
            True,
            confidence=1.0,
            source="episode",
            metadata={
                "episode_action": episode.action,
                "original_text": episode.original_text,
            },
        )

    def _extract_close_app(
        self,
        episode: Episode,
    ) -> SemanticFact | None:
        application = self._extract_application(
            episode
        )

        if not application:
            return None

        return self._semantic_memory.learn(
            application,
            "es una aplicación",
            True,
            confidence=1.0,
            source="episode",
            metadata={
                "episode_action": episode.action,
                "original_text": episode.original_text,
            },
        )

    def _extract_volume(
        self,
        episode: Episode,
    ) -> SemanticFact | None:
        parameters = episode.parameters

        if not isinstance(parameters, dict):
            parameters = {}

        level = parameters.get("level")

        if level is None:
            output = episode.output

            if isinstance(output, dict):
                level = output.get("level")

        if level is None:
            return None

        try:
            level = float(level)
        except (
            TypeError,
            ValueError,
        ):
            return None

        if level.is_integer():
            level = int(level)

        return self._semantic_memory.learn(
            "system",
            "último volumen conocido",
            level,
            confidence=1.0,
            source="episode",
            metadata={
                "episode_action": episode.action,
                "original_text": episode.original_text,
            },
        )

    @staticmethod
    def _extract_application(
        episode: Episode,
    ) -> str | None:
        parameters = episode.parameters

        if isinstance(parameters, dict):
            for key in (
                "application",
                "app",
                "name",
            ):
                value = parameters.get(key)

                if isinstance(value, str) and value.strip():
                    return value.strip()

        output = episode.output

        if isinstance(output, dict):
            for key in (
                "application",
                "app",
                "name",
            ):
                value = output.get(key)

                if isinstance(value, str) and value.strip():
                    return value.strip()

        return None
