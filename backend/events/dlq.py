import uuid
import json
from datetime import datetime

from core.database import get_connection
from events.bus import bus


class DeadLetterQueue:

    async def handle_final_failure(self, payload):

        conn = get_connection()
        cur = conn.cursor()

        cur.execute("""
        INSERT INTO dead_jobs
        (id, job_id, workflow, tenant_id, workspace_id,
         error, payload, created_at)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            str(uuid.uuid4()),
            payload.get("job_id"),
            payload.get("workflow"),
            payload.get("tenant_id"),
            payload.get("workspace_id"),
            payload.get("error"),
            json.dumps(payload),
            datetime.utcnow()
        ))

        conn.commit()
        conn.close()

        await bus.publish("dlq.stored", {
            "workflow": payload.get("workflow"),
            "job_id": payload.get("job_id")
        })


dlq = DeadLetterQueue()


def register_dlq():
    bus.subscribe("job.failed.final", dlq.handle_final_failure)