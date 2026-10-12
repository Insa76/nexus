from __future__ import annotations

from context.models import AssistantContext
from context.store import ContextStore


class ContextResolver:
    """
    Frontera de resolución del contexto operativo de NEXUS.

    El resolver no almacena usuarios, organizaciones ni proyectos.
    Tampoco conoce el Engine.

    Su única responsabilidad es transformar una selección de contexto
    en un AssistantContext utilizando el ContextStore.
    """

    def __init__(self, store: ContextStore) -> None:
        self._store = store

    def resolve(
        self,
        *,
        user_id: str | None = None,
        organization_id: str | None = None,
    ) -> AssistantContext:
        """
        Resuelve el contexto seleccionado por la capa superior.

        La lógica de selección y aislamiento permanece en ContextStore.
        """

        return self._store.build_context(
            user_id=user_id,
            organization_id=organization_id,
        )
