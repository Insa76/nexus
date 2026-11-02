from events.bus import bus
from jobs.manager import manager
from workflows.repository import get_workflows_by_trigger


async def handle_event(event_type: str, payload: dict):

    workflows = get_workflows_by_trigger(event_type)

    for wf in workflows:

        await manager.create_job(
            wf["name"],
            wf["tenant_id"],
            wf["workspace_id"]
        )


def register_event_routes():

    bus.subscribe("filesystem.created", handle_event)
    bus.subscribe("webhook.received", handle_event)
    bus.subscribe("system.event", handle_event)

    # internos
    bus.subscribe("job.failed", handle_event)
    bus.subscribe("job.done", handle_event)
    bus.subscribe("step.error", handle_event)
    bus.subscribe("circuit.opened", handle_event)
    bus.subscribe("circuit.closed", handle_event)