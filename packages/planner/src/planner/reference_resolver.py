from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class Reference:
    """
    Referencia contextual resuelta por NEXUS.

    kind:
        Tipo de objeto al que hace referencia el usuario.

    value:
        Valor concreto asociado a la referencia.

    confidence:
        Confianza de la resolución.

    source:
        Origen del dato contextual.
    """

    kind: str
    value: Any
    confidence: float = 1.0
    source: str = "context"


class ReferenceResolver:
    """
    Resuelve referencias contextuales utilizando el contexto
    cognitivo construido por NEXUS.

    Este componente NO decide qué acción ejecutar.

    Su única responsabilidad es determinar si una expresión
    hace referencia de manera suficientemente segura a un
    objeto conocido del contexto.
    """

    _APPLICATION_REFERENCES = {
        "esa aplicación",
        "esa app",
        "la aplicación",
        "la app",
        "esa aplicacion",
        "la aplicacion",
    }

    _CAPTURE_REFERENCES = {
        "esa captura",
        "la captura",
        "esa pantalla",
        "la pantalla",
    }

    _VOLUME_REFERENCES = {
        "el volumen",
        "el sonido",
        "el audio",
    }

    _PREVIOUS_ACTION_REFERENCES = {
        "eso",
        "lo mismo",
        "esa acción",
        "esa accion",
    }

    def resolve(
        self,
        text: str,
        context: dict[str, Any] | None = None,
    ) -> Reference | None:
        """
        Resuelve una referencia contextual.

        Devuelve None cuando:
        - no existe contexto suficiente;
        - la expresión no corresponde a una referencia conocida;
        - existe una referencia pero no hay evidencia suficiente
          para resolverla.
        """

        if not text or not context:
            return None

        normalized = self._normalize(text)
        references = context.get("references", {})

        if not isinstance(references, dict):
            return None

        application = self._resolve_application(
            normalized,
            references,
        )

        if application is not None:
            return application

        capture = self._resolve_capture(
            normalized,
            references,
        )

        if capture is not None:
            return capture

        volume = self._resolve_volume(
            normalized,
            references,
        )

        if volume is not None:
            return volume

        previous_action = self._resolve_previous_action(
            normalized,
            references,
        )

        if previous_action is not None:
            return previous_action

        return None

    @staticmethod
    def _normalize(text: str) -> str:
        return " ".join(
            text.lower().strip().split()
        )

    def _resolve_application(
        self,
        normalized: str,
        references: dict[str, Any],
    ) -> Reference | None:

        if normalized not in self._APPLICATION_REFERENCES:
            return None

        application = references.get(
            "last_executed_application"
        )

        if not isinstance(application, str):
            application = references.get(
                "last_application"
            )

        if not isinstance(application, str):
            return None

        application = application.strip()

        if not application:
            return None

        return Reference(
            kind="application",
            value=application,
            confidence=1.0,
            source="last_executed_application",
        )

    def _resolve_capture(
        self,
        normalized: str,
        references: dict[str, Any],
    ) -> Reference | None:

        if normalized not in self._CAPTURE_REFERENCES:
            return None

        if references.get(
            "last_capture_available"
        ) is not True:
            return None

        return Reference(
            kind="capture",
            value=True,
            confidence=1.0,
            source="last_capture_available",
        )

    def _resolve_volume(
        self,
        normalized: str,
        references: dict[str, Any],
    ) -> Reference | None:

        if normalized not in self._VOLUME_REFERENCES:
            return None

        volume = references.get(
            "last_volume"
        )

        if volume is None:
            return None

        try:
            volume = float(volume)
        except (TypeError, ValueError):
            return None

        return Reference(
            kind="volume",
            value=volume,
            confidence=1.0,
            source="last_volume",
        )

    def _resolve_previous_action(
        self,
        normalized: str,
        references: dict[str, Any],
    ) -> Reference | None:

        if normalized not in self._PREVIOUS_ACTION_REFERENCES:
            return None

        action = references.get(
            "last_action"
        )

        if not isinstance(action, str):
            return None

        action = action.strip()

        if not action:
            return None

        return Reference(
            kind="action",
            value=action,
            confidence=1.0,
            source="last_action",
        )
