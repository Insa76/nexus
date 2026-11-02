import asyncio
from collections import defaultdict
from events.bus import bus
from jobs.manager import manager
from workflows.repository import get_workflow_by_name


class RetryManager:

    def __init__(self):
        self.retry_count = defaultdict(int)

    async def handle_step_error(self, payload):

        workflow = payload["workflow"]
        job_id = payload.get("job_id")

        wf = get_workflow_by_name(workflow)

        if not wf:
            return

        retry_conf = wf.get("retry")
        if not retry_conf:
            return

        max_r = retry_conf.get("max_retries", 0)
        delay = retry_conf.get("delay_seconds", 0)
        backoff = retry_conf.get("backoff", "fixed")

        self.retry_count[job_id] += 1
        attempt = self.retry_count[job_id]

        if attempt > max_r:

            # 🔥 AQUÍ VA EL PASO 4
            await bus.publish("job.failed.final", {
                "workflow": workflow,
                "job_id": job_id,
                "tenant_id": wf.get("tenant_id"),
                "workspace_id": wf.get("workspace_id"),
                "error": "Max retries exceeded"
            })

            return

        # delay inteligente
        if backoff == "exponential":
            wait = delay * (2 ** (attempt - 1))
        else:
            wait = delay

        await asyncio.sleep(wait)

        await manager.create_job(
            workflow,
            wf.get("tenant_id"),
            wf.get("workspace_id")
        )


retry_manager = RetryManager()


def register_retry():
    bus.subscribe("step.error", retry_manager.handle_step_error)