from datetime import datetime, timezone

from context import (
    AssistantContext,
    OrganizationProfile,
    ProjectContext,
    UserProfile,
)

from tasks import Reminder, ReminderResolver, ReminderStore


TRIGGER_AT = datetime(
    2026,
    9,
    21,
    9,
    0,
    tzinfo=timezone.utc,
)


def test_resolver_returns_user_reminders() -> None:
    user = UserProfile.create(
        name="Diego",
    )

    context = AssistantContext(
        user=user,
    )

    matching = Reminder.create(
        message="Recordatorio del usuario",
        trigger_at=TRIGGER_AT,
        user_id=user.id,
    )

    unrelated = Reminder.create(
        message="Otro usuario",
        trigger_at=TRIGGER_AT,
        user_id="other-user",
    )

    store = ReminderStore()
    store.add(matching)
    store.add(unrelated)

    resolver = ReminderResolver(store)

    assert resolver.resolve(context) == [matching]


def test_resolver_returns_organization_reminders() -> None:
    organization = OrganizationProfile.create(
        name="Paraná Agency",
    )

    context = AssistantContext(
        organization=organization,
    )

    matching = Reminder.create(
        message="Recordatorio de la organización",
        trigger_at=TRIGGER_AT,
        organization_id=organization.id,
    )

    unrelated = Reminder.create(
        message="Otra organización",
        trigger_at=TRIGGER_AT,
        organization_id="other-organization",
    )

    store = ReminderStore()
    store.add(matching)
    store.add(unrelated)

    resolver = ReminderResolver(store)

    assert resolver.resolve(context) == [matching]


def test_resolver_returns_project_reminders() -> None:
    organization = OrganizationProfile.create(
        name="Paraná Agency",
    )

    project = ProjectContext.create(
        name="ORBIT",
        organization_id=organization.id,
    )

    context = AssistantContext(
        organization=organization,
        projects=(project,),
    )

    matching = Reminder.create(
        message="Recordatorio de ORBIT",
        trigger_at=TRIGGER_AT,
        project_id=project.id,
    )

    unrelated = Reminder.create(
        message="Otro proyecto",
        trigger_at=TRIGGER_AT,
        project_id="other-project",
    )

    store = ReminderStore()
    store.add(matching)
    store.add(unrelated)

    resolver = ReminderResolver(store)

    assert resolver.resolve(context) == [matching]


def test_resolver_combines_context_reminders() -> None:
    user = UserProfile.create(
        name="Diego",
    )

    organization = OrganizationProfile.create(
        name="Paraná Agency",
    )

    project = ProjectContext.create(
        name="ORBIT",
        organization_id=organization.id,
    )

    context = AssistantContext(
        user=user,
        organization=organization,
        projects=(project,),
    )

    user_reminder = Reminder.create(
        message="Recordatorio personal",
        trigger_at=TRIGGER_AT,
        user_id=user.id,
    )

    organization_reminder = Reminder.create(
        message="Recordatorio de agencia",
        trigger_at=TRIGGER_AT,
        organization_id=organization.id,
    )

    project_reminder = Reminder.create(
        message="Recordatorio de ORBIT",
        trigger_at=TRIGGER_AT,
        project_id=project.id,
    )

    unrelated = Reminder.create(
        message="Recordatorio externo",
        trigger_at=TRIGGER_AT,
        user_id="other-user",
        organization_id="other-organization",
        project_id="other-project",
    )

    store = ReminderStore()

    for reminder in (
        user_reminder,
        organization_reminder,
        project_reminder,
        unrelated,
    ):
        store.add(reminder)

    resolver = ReminderResolver(store)

    assert resolver.resolve(context) == [
        user_reminder,
        organization_reminder,
        project_reminder,
    ]


def test_resolver_returns_empty_for_empty_context() -> None:
    context = AssistantContext()

    store = ReminderStore()

    store.add(
        Reminder.create(
            message="Sin contexto",
            trigger_at=TRIGGER_AT,
        )
    )

    resolver = ReminderResolver(store)

    assert resolver.resolve(context) == []


def test_resolver_does_not_mutate_store() -> None:
    user = UserProfile.create(
        name="Diego",
    )

    context = AssistantContext(
        user=user,
    )

    reminder = Reminder.create(
        message="Recordatorio",
        trigger_at=TRIGGER_AT,
        user_id=user.id,
    )

    store = ReminderStore()
    store.add(reminder)

    resolver = ReminderResolver(store)

    resolved = resolver.resolve(context)

    assert resolved == [reminder]
    assert store.list() == [reminder]
    assert store.count() == 1
