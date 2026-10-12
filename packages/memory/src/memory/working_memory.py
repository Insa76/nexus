from __future__ import annotations

from uuid import uuid4
from typing import Iterable

from memory.memory_entry import MemoryEntry


class WorkingMemory:
    """
    Memoria temporal de la sesión actual de NEXUS.

    Almacena los eventos recientes de la interacción
    y permite recuperar el contexto inmediato.
    """

    def __init__(
        self,
        max_entries: int = 100,
    ) -> None:

        if max_entries <= 0:
            raise ValueError(
                "max_entries must be greater than zero."
            )

        self._max_entries = max_entries

        self._entries: list[MemoryEntry] = []

    def add(
        self,
        type: str,
        data: dict,
    ) -> MemoryEntry:
        """
        Agrega una nueva entrada a la memoria.
        """

        entry = MemoryEntry(
            id=str(uuid4()),
            type=type,
            data=data,
        )

        self._entries.append(
            entry
        )

        self._trim()

        return entry

    def add_entry(
        self,
        entry: MemoryEntry,
    ) -> MemoryEntry:
        """
        Agrega una entrada existente.
        """

        self._entries.append(
            entry
        )

        self._trim()

        return entry

    def recent(
        self,
        limit: int = 10,
    ) -> list[MemoryEntry]:
        """
        Devuelve las entradas más recientes.
        """

        if limit <= 0:
            return []

        return self._entries[-limit:]

    def last(self) -> MemoryEntry | None:
        """
        Devuelve la última entrada registrada.
        """

        if not self._entries:
            return None

        return self._entries[-1]

    def find(
        self,
        type: str,
    ) -> list[MemoryEntry]:
        """
        Devuelve todas las entradas de un tipo.
        """

        return [
            entry
            for entry in self._entries
            if entry.type == type
        ]

    def count(self) -> int:
        """
        Devuelve la cantidad de entradas almacenadas.
        """

        return len(
            self._entries
        )

    def all(self) -> list[MemoryEntry]:
        """
        Devuelve una copia de todas las entradas.
        """

        return list(
            self._entries
        )

    def clear(self) -> None:
        """
        Limpia completamente la memoria.
        """

        self._entries.clear()

    def _trim(self) -> None:
        """
        Mantiene la memoria dentro del límite configurado.
        """

        overflow = (
            len(self._entries)
            - self._max_entries
        )

        if overflow > 0:

            del self._entries[
                :overflow
            ]
