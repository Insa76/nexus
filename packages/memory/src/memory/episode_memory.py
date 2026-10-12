from __future__ import annotations

from typing import Any

from memory.episode import Episode
from memory.working_memory import WorkingMemory


class EpisodeMemory:
    """
    Capa de memoria episódica de NEXUS.

    Utiliza WorkingMemory como almacenamiento subyacente.

    No interpreta intenciones.
    No ejecuta acciones.
    No genera lenguaje natural.
    """

    _ENTRY_TYPE = "episode"

    def __init__(
        self,
        memory: WorkingMemory,
    ) -> None:

        self._memory = memory

    def add(
        self,
        episode: Episode,
    ) -> Episode:
        """
        Registra un episodio en WorkingMemory.
        """

        self._memory.add(
            self._ENTRY_TYPE,
            episode.model_dump(),
        )

        return episode

    def recent(
        self,
        limit: int = 10,
    ) -> list[Episode]:
        """
        Devuelve los episodios más recientes.
        """

        if limit <= 0:
            return []

        entries = self._memory.find(
            self._ENTRY_TYPE
        )

        entries = entries[-limit:]

        return [
            Episode.model_validate(
                entry.data
            )
            for entry in entries
        ]

    def last(self) -> Episode | None:
        """
        Devuelve el último episodio registrado.
        """

        episodes = self.recent(
            limit=1
        )

        if not episodes:
            return None

        return episodes[0]

    def previous(self) -> Episode | None:
        """
        Devuelve el episodio anterior al último
        episodio registrado.

        Si existe solamente un episodio, devuelve None.
        """

        entries = self._memory.find(
            self._ENTRY_TYPE
        )

        if len(entries) < 2:
            return None

        entry = entries[-2]

        return Episode.model_validate(
            entry.data
        )

    def find_by_action(
        self,
        action: str,
        limit: int = 1,
    ) -> list[Episode]:
        """
        Busca episodios exitosos de una acción concreta.

        Los resultados se devuelven desde el más reciente
        hacia atrás.

        Esta capa solamente consulta memoria. No interpreta
        la consulta del usuario.
        """

        if not action or limit <= 0:
            return []

        normalized_action = action.strip()

        if not normalized_action:
            return []

        entries = self._memory.find(
            self._ENTRY_TYPE
        )

        matches: list[Episode] = []

        for entry in reversed(entries):

            try:
                episode = Episode.model_validate(
                    entry.data
                )
            except Exception:
                continue

            if not episode.success:
                continue

            if episode.action != normalized_action:
                continue

            matches.append(
                episode
            )

            if len(matches) >= limit:
                break

        return matches

    def find_latest_by_action(
        self,
        action: str,
    ) -> Episode | None:
        """
        Devuelve el episodio exitoso más reciente
        correspondiente a una acción.
        """

        matches = self.find_by_action(
            action,
            limit=1,
        )

        if not matches:
            return None

        return matches[0]

    def find_parameter(
        self,
        action: str,
        parameter: str,
    ) -> Any | None:
        """
        Busca un parámetro dentro del episodio exitoso
        más reciente de una acción.

        Devuelve None si el episodio o el parámetro
        no existen.
        """

        if not parameter:
            return None

        episode = self.find_latest_by_action(
            action
        )

        if episode is None:
            return None

        parameters = episode.parameters

        if not isinstance(
            parameters,
            dict,
        ):
            return None

        return parameters.get(
            parameter
        )

    def count(self) -> int:
        """
        Devuelve la cantidad de episodios registrados.
        """

        return len(
            self._memory.find(
                self._ENTRY_TYPE
            )
        )

    def clear(self) -> None:
        """
        Elimina todos los episodios.

        No limpia el resto de WorkingMemory.
        """

        entries = self._memory.find(
            self._ENTRY_TYPE
        )

        if not entries:
            return

        episode_ids = {
            entry.id
            for entry in entries
        }

        self._memory._entries = [
            entry
            for entry in self._memory.all()
            if entry.id not in episode_ids
        ]
