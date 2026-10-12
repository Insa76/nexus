from context import (
    ContextStore,
    OrganizationProfile,
    ProjectContext,
    UserProfile,
)


def test_user_organization_and_project_context() -> None:
    store = ContextStore()

    organization = OrganizationProfile.create(
        "Estudio Jurídico Demo",
        industry="legal",
        areas=("Civil", "Comercial"),
        rules=("Los contratos requieren revisión antes de firma.",),
        priorities=("Vencimientos", "Clientes"),
    )

    user = UserProfile.create(
        "Diego",
        role="Abogado",
        organization_id=organization.id,
        responsibilities=("Revisión contractual",),
        priorities=("Vencimientos",),
    )

    project = ProjectContext.create(
        "Cliente Demo",
        organization.id,
        description="Proyecto de prueba.",
        responsible_user_ids=(user.id,),
    )

    store.add_organization(organization)
    store.add_user(user)
    store.add_project(project)

    context = store.build_context(user_id=user.id)

    assert context.user is user
    assert context.organization is organization
    assert len(context.projects) == 1
    assert context.projects[0] is project
    assert context.projects[0].name == "Cliente Demo"


def test_context_can_be_built_from_organization() -> None:
    store = ContextStore()

    organization = OrganizationProfile.create(
        "Constructora Demo",
        industry="construction",
    )

    project = ProjectContext.create(
        "Obra Norte",
        organization.id,
    )

    store.add_organization(organization)
    store.add_project(project)

    context = store.build_context(
        organization_id=organization.id,
    )

    assert context.user is None
    assert context.organization is organization
    assert context.projects == (project,)


def test_project_lookup() -> None:
    store = ContextStore()

    organization = OrganizationProfile.create(
        "Agencia Demo",
        industry="marketing",
    )

    project = ProjectContext.create(
        "Campaña 2026",
        organization.id,
    )

    store.add_project(project)

    assert store.get_project(project.id) is project
    assert store.get_project("missing") is None


def test_explicit_organization_selection_has_priority() -> None:
    store = ContextStore()

    organization_a = OrganizationProfile.create(
        "Organización A",
        industry="legal",
    )

    organization_b = OrganizationProfile.create(
        "Organización B",
        industry="technology",
    )

    user = UserProfile.create(
        "Diego",
        organization_id=organization_a.id,
    )

    project_a = ProjectContext.create(
        "Proyecto A",
        organization_a.id,
    )

    project_b = ProjectContext.create(
        "Proyecto B",
        organization_b.id,
    )

    store.add_organization(organization_a)
    store.add_organization(organization_b)
    store.add_user(user)
    store.add_project(project_a)
    store.add_project(project_b)

    context = store.build_context(
        user_id=user.id,
        organization_id=organization_b.id,
    )

    assert context.user is user
    assert context.organization is organization_b
    assert context.projects == (project_b,)


def test_projects_are_isolated_by_organization() -> None:
    store = ContextStore()

    organization_a = OrganizationProfile.create(
        "Organización A",
    )

    organization_b = OrganizationProfile.create(
        "Organización B",
    )

    project_a = ProjectContext.create(
        "Proyecto A",
        organization_a.id,
    )

    project_b = ProjectContext.create(
        "Proyecto B",
        organization_b.id,
    )

    store.add_organization(organization_a)
    store.add_organization(organization_b)
    store.add_project(project_a)
    store.add_project(project_b)

    context = store.build_context(
        organization_id=organization_a.id,
    )

    assert context.projects == (project_a,)
    assert project_b not in context.projects


def test_missing_identifiers_produce_partial_or_empty_context() -> None:
    store = ContextStore()

    context = store.build_context(
        user_id="missing-user",
        organization_id="missing-organization",
    )

    assert context.user is None
    assert context.organization is None
    assert context.projects == ()


def test_empty_selection_returns_empty_context() -> None:
    store = ContextStore()

    context = store.build_context()

    assert context.user is None
    assert context.organization is None
    assert context.projects == ()
