from context import (
    ContextResolver,
    ContextStore,
    OrganizationProfile,
    ProjectContext,
    UserProfile,
)


def test_resolver_builds_context_from_user() -> None:
    store = ContextStore()
    resolver = ContextResolver(store)

    organization = OrganizationProfile.create(
        "Organización Demo",
        industry="technology",
    )

    user = UserProfile.create(
        "Diego",
        role="Administrador",
        organization_id=organization.id,
    )

    project = ProjectContext.create(
        "Proyecto Demo",
        organization.id,
    )

    store.add_organization(organization)
    store.add_user(user)
    store.add_project(project)

    context = resolver.resolve(user_id=user.id)

    assert context.user is user
    assert context.organization is organization
    assert context.projects == (project,)


def test_resolver_can_select_explicit_organization() -> None:
    store = ContextStore()
    resolver = ContextResolver(store)

    organization_a = OrganizationProfile.create(
        "Organización A",
    )

    organization_b = OrganizationProfile.create(
        "Organización B",
    )

    user = UserProfile.create(
        "Diego",
        organization_id=organization_a.id,
    )

    project_b = ProjectContext.create(
        "Proyecto B",
        organization_b.id,
    )

    store.add_organization(organization_a)
    store.add_organization(organization_b)
    store.add_user(user)
    store.add_project(project_b)

    context = resolver.resolve(
        user_id=user.id,
        organization_id=organization_b.id,
    )

    assert context.user is user
    assert context.organization is organization_b
    assert context.projects == (project_b,)


def test_resolver_returns_empty_context_without_selection() -> None:
    store = ContextStore()
    resolver = ContextResolver(store)

    context = resolver.resolve()

    assert context.user is None
    assert context.organization is None
    assert context.projects == ()
