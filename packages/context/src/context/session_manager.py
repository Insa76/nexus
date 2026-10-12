from __future__ import annotations

from context.models import AssistantContext
from context.session import AssistantSession


class AssistantSessionManager:
    """
    Administra el ciclo de vida de una sesión Assistant activa.

    El manager no resuelve contexto ni persiste sesiones.
    Su única responsabilidad es crear, exponer y cerrar
    la sesión activa.
    """

    def __init__(self) -> None:
        self._active_session: AssistantSession | None = None

    def start(
        self,
        context: AssistantContext,
    ) -> AssistantSession:
        """
        Crea una nueva sesión y la establece como activa.
        """

        session = AssistantSession.create(context)
        self._active_session = session

        return session

    def get_active(self) -> AssistantSession | None:
        """
        Devuelve la sesión actualmente activa.
        """

        return self._active_session

    def close(self) -> AssistantSession | None:
        """
        Cierra la sesión activa y devuelve la sesión que estaba activa.
        """

        session = self._active_session
        self._active_session = None

        return session
