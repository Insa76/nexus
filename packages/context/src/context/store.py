from __future__ import annotations

from context.models import (
    AssistantContext,
    OrganizationProfile,
    ProjectContext,
    UserProfile,
)


class ContextStore:
    """
    Almacén en memoria para el contexto operativo de NEXUS.

    Su responsabilidad es resolver el contexto de una capa superior
    sin introducir lógica de contexto dentro del Engine.

    Flujo:

        ContextStore
            ↓
        AssistantContext
            ↓
        User / Organization / Projects

    El almacenamiento es deliberadamente en memoria en esta fase.
    """

    def __init__(self) -> None:
        self._users: dict[str, UserProfile] = {}
        self._organizations: dict[str, OrganizationProfile] = {}
        self._projects: dict[str, ProjectContext] = {}

    def add_user(self, user: UserProfile) -> None:
        self._users[user.id] = user

    def add_organization(
        self,
        organization: OrganizationProfile,
    ) -> None:
        self._organizations[organization.id] = organization

    def add_project(self, project: ProjectContext) -> None:
        self._projects[project.id] = project

    def get_user(self, user_id: str) -> UserProfile | None:
        return self._users.get(user_id)

    def get_organization(
        self,
        organization_id: str,
    ) -> OrganizationProfile | None:
        return self._organizations.get(organization_id)

    def get_project(self, project_id: str) -> ProjectContext | None:
        return self._projects.get(project_id)

    def projects_for_organization(
        self,
        organization_id: str,
    ) -> tuple[ProjectContext, ...]:
        return tuple(
            project
            for project in self._projects.values()
            if project.organization_id == organization_id
        )

    def build_context(
        self,
        *,
        user_id: str | None = None,
        organization_id: str | None = None,
    ) -> AssistantContext:
        """
        Construye un AssistantContext a partir de los identificadores
        seleccionados por la capa superior.

        Reglas:

        - user_id selecciona al usuario.
        - Si no se especifica organization_id, se utiliza la organización
          asociada al usuario.
        - Si organization_id se especifica explícitamente, tiene prioridad
          sobre la organización asociada al usuario.
        - Los proyectos siempre se limitan a la organización finalmente
          seleccionada.
        - IDs inexistentes no generan errores; simplemente producen un
          contexto parcial o vacío.
        """

        user = (
            self.get_user(user_id)
            if user_id is not None
            else None
        )

        selected_organization_id = organization_id

        if selected_organization_id is None and user is not None:
            selected_organization_id = user.organization_id

        organization = (
            self.get_organization(selected_organization_id)
            if selected_organization_id is not None
            else None
        )

        projects = (
            self.projects_for_organization(organization.id)
            if organization is not None
            else ()
        )

        return AssistantContext(
            user=user,
            organization=organization,
            projects=projects,
        )
