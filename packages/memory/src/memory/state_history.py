from __future__ import annotations

from typing import Any

from memory.working_memory import WorkingMemory


class StateHistory:
    """
    Consulta estados históricos derivados de los
    execution_result almacenados en WorkingMemory.

    No modifica la memoria.
    No ejecuta acciones.
    No interpreta lenguaje natural.

    Distingue entre:

    - eventos de cambio de estado
    - eventos de restauración
    - último estado conocido
    - estado anterior al último cambio/restauración
    - último estado establecido explícitamente

    La clase solamente reconstruye estados a partir
    de resultados reales de ejecución.
    """

    STATE_CHANGING_STATUSES = {
        "set",
        "opened",
        "closed",
        "enabled",
        "disabled",
        "connected",
        "disconnected",
        "started",
        "stopped",
        "muted",
        "unmuted",
        "restored",
    }

    RESTORATION_STATUS = "restored"

    def __init__(
        self,
        memory: WorkingMemory,
    ) -> None:

        self._memory = memory

    def events(
        self,
        resource: str,
        status: str | None = None,
    ) -> list[dict[str, Any]]:
        """
        Devuelve todos los eventos históricos válidos
        de un recurso.

        Si se especifica status, filtra por ese estado.
        """

        events: list[dict[str, Any]] = []

        for entry in self._memory.find(
            "execution_result"
        ):

            data = entry.data

            if not data.get("success"):
                continue

            output = data.get(
                "output",
                {},
            )

            if not isinstance(
                output,
                dict,
            ):
                continue

            if resource not in output:
                continue

            event_status = output.get(
                "status"
            )

            if (
                event_status
                not in self.STATE_CHANGING_STATUSES
            ):
                continue

            if (
                status is not None
                and event_status != status
            ):
                continue

            events.append(
                {
                    "resource": resource,
                    "value": output[resource],
                    "status": event_status,
                    "timestamp": entry.timestamp,
                    "data": data,
                }
            )

        return events

    def values(
        self,
        resource: str,
        status: str | None = None,
    ) -> list[Any]:
        """
        Devuelve los valores históricos de un recurso.

        Incluye eventos de restauración salvo que se
        solicite explícitamente otro status.
        """

        return [
            event["value"]
            for event in self.events(
                resource,
                status=status,
            )
        ]

    def last(
        self,
        resource: str,
        status: str | None = None,
    ) -> Any | None:
        """
        Devuelve el último valor conocido de un recurso.

        Si se especifica status, devuelve el último
        evento que tenga ese status.
        """

        events = self.events(
            resource,
            status=status,
        )

        if not events:
            return None

        return events[-1]["value"]

    def previous(
        self,
        resource: str,
        status: str | None = None,
    ) -> Any | None:
        """
        Devuelve el valor anterior al último evento.

        Si se especifica status, solamente considera
        eventos de ese tipo.
        """

        events = self.events(
            resource,
            status=status,
        )

        if len(events) < 2:
            return None

        return events[-2]["value"]

    def last_event(
        self,
        resource: str,
        status: str | None = None,
    ) -> dict[str, Any] | None:
        """
        Devuelve el último evento conocido.
        """

        events = self.events(
            resource,
            status=status,
        )

        if not events:
            return None

        return events[-1]

    def previous_event(
        self,
        resource: str,
        status: str | None = None,
    ) -> dict[str, Any] | None:
        """
        Devuelve el evento anterior al último.
        """

        events = self.events(
            resource,
            status=status,
        )

        if len(events) < 2:
            return None

        return events[-2]

    def last_set(
        self,
        resource: str,
    ) -> Any | None:
        """
        Devuelve el último valor establecido explícitamente.

        No considera restauraciones.
        """

        return self.last(
            resource,
            status="set",
        )

    def previous_set(
        self,
        resource: str,
    ) -> Any | None:
        """
        Devuelve el valor establecido explícitamente
        inmediatamente anterior al último set.

        No considera restauraciones.
        """

        return self.previous(
            resource,
            status="set",
        )

    def last_non_restored(
        self,
        resource: str,
    ) -> Any | None:
        """
        Devuelve el último estado que no provino
        de una restauración.

        Es útil para reconstruir el estado base
        anterior a una operación de restore.
        """

        events = self.events(
            resource
        )

        for event in reversed(events):

            if (
                event["status"]
                != self.RESTORATION_STATUS
            ):
                return event["value"]

        return None

    def previous_non_restored(
        self,
        resource: str,
    ) -> Any | None:
        """
        Devuelve el estado no restaurado anterior
        al último estado no restaurado.
        """

        events = [
            event
            for event in self.events(resource)
            if (
                event["status"]
                != self.RESTORATION_STATUS
            )
        ]

        if len(events) < 2:
            return None

        return events[-2]["value"]

    def previous_restorable(
        self,
        resource: str,
    ) -> Any | None:
        """
        Devuelve el estado al que debería volver
        una operación de restauración.

        Si el último evento fue una restauración,
        busca el último estado anterior que no sea
        una restauración.

        Si el último evento no fue una restauración,
        devuelve el estado inmediatamente anterior.
        """

        events = self.events(
            resource
        )

        if not events:
            return None

        last_event = events[-1]

        #
        # Si el último evento fue una restauración,
        # buscamos hacia atrás el último estado que
        # no provenga de otra restauración.
        #

        if (
            last_event["status"]
            == self.RESTORATION_STATUS
        ):

            for event in reversed(
                events[:-1]
            ):

                if (
                    event["status"]
                    != self.RESTORATION_STATUS
                ):
                    return event["value"]

            return None

        #
        # Todavía no hubo restauración.
        # En ese caso queremos el estado anterior
        # al estado actual.
        #

        if len(events) < 2:
            return None

        return events[-2]["value"]

    def find(
        self,
        resource: str,
        value: Any,
        status: str | None = None,
    ) -> bool:
        """
        Indica si un valor determinado aparece
        en el historial del recurso.
        """

        return value in self.values(
            resource,
            status=status,
        )

    def find_events(
        self,
        resource: str,
        value: Any,
        status: str | None = None,
    ) -> list[dict[str, Any]]:
        """
        Devuelve todos los eventos que coincidan
        con un valor determinado.
        """

        return [
            event
            for event in self.events(
                resource,
                status=status,
            )
            if event["value"] == value
        ]
