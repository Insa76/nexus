from fastapi import APIRouter
from jobs.manager import manager
from events.bus import bus

router = APIRouter(prefix="/webhook")


@router.post("/{workflow_name}")
async def webhook_trigger(workflow_name: str):

    await bus.publish("webhook.received", {
        "workflow": workflow_name
    })

    return {"status": "event published"}