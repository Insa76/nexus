from __future__ import annotations

from context.models import AssistantContext


def project_ids_for_context(
    context: AssistantContext,
) -> frozenset[str]:
    """
    Devuelve los proyectos visibles para el contexto operativo.

    Si metadata contiene active_project_id, la selección es explícita:
    solo ese proyecto queda en alcance; null significa sin proyecto activo.
    Los contextos anteriores a esta selección no incluyen la clave y
    conservan el comportamiento compatible de considerar todos los proyectos.
    """
    projects = {project.id for project in context.projects}

    if "active_project_id" not in context.metadata:
        return frozenset(projects)

    active_project_id = context.metadata.get("active_project_id")
    if not isinstance(active_project_id, str):
        return frozenset()

    if active_project_id not in projects:
        return frozenset()

    return frozenset({active_project_id})
