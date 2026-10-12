from bootstrap.assistant_services import (
    AssistantServices,
    build_assistant_services,
)


def test_build_assistant_services() -> None:
    services = build_assistant_services()

    assert isinstance(services, AssistantServices)

    assert services.scheduler is not None
    assert services.reminder_store is not None
    assert services.temporal_scheduler is not None
    assert services.reminder_scheduler is not None


def test_reminder_scheduler_uses_shared_services() -> None:
    services = build_assistant_services()

    assert (
        services.reminder_scheduler._reminder_store
        is services.reminder_store
    )

    assert (
        services.reminder_scheduler._scheduler_adapter
        is services.temporal_scheduler
    )
