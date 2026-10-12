from __future__ import annotations

from dataclasses import dataclass

from runtime.scheduler import Scheduler
from tasks import ReminderStore

from bootstrap.reminder_scheduler import ReminderScheduler
from bootstrap.temporal_scheduler import TemporalSchedulerAdapter


@dataclass(slots=True)
class AssistantServices:
    """
    Servicios operativos del Assistant Layer.

    Agrupa las dependencias de dominio e infraestructura que
    pertenecen a las capacidades auxiliares de NEXUS.

    No contiene lógica cognitiva.
    """

    scheduler: Scheduler
    reminder_store: ReminderStore
    temporal_scheduler: TemporalSchedulerAdapter
    reminder_scheduler: ReminderScheduler


def build_assistant_services() -> AssistantServices:
    """
    Construye los servicios del Assistant Layer.
    """

    scheduler = Scheduler()

    reminder_store = ReminderStore()

    temporal_scheduler = TemporalSchedulerAdapter(
        scheduler
    )

    reminder_scheduler = ReminderScheduler(
        scheduler_adapter=temporal_scheduler,
        reminder_store=reminder_store,
    )

    return AssistantServices(
        scheduler=scheduler,
        reminder_store=reminder_store,
        temporal_scheduler=temporal_scheduler,
        reminder_scheduler=reminder_scheduler,
    )
