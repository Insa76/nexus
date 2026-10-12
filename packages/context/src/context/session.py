from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from uuid import uuid4

from context.models import AssistantContext


@dataclass(frozen=True)
class AssistantSession:
    """
    Sesión activa de la capa Assistant de NEXUS.

    Una sesión representa el contexto operativo seleccionado para
    una interacción determinada.

    No resuelve contexto, no accede al ContextStore y no contiene
    memoria cognitiva.
    """

    session_id: str
    context: AssistantContext
    created_at: datetime

    @classmethod
    def create(
        cls,
        context: AssistantContext,
    ) -> AssistantSession:
        return cls(
            session_id=str(uuid4()),
            context=context,
            created_at=datetime.now(timezone.utc),
        )
