import uuid
import json
from datetime import datetime

from core.database import get_connection


def log_event(
    user,
    action,
    entity=None,
    entity_id=None,
    metadata=None
):

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
    INSERT INTO audit_logs
    (id, user_id, tenant_id, workspace_id, action,
     entity, entity_id, metadata, created_at)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
    """, (
        str(uuid.uuid4()),
        user.get("user_id"),
        user.get("tenant_id"),
        user.get("workspace_id"),
        action,
        entity,
        entity_id,
        json.dumps(metadata or {}),
        datetime.utcnow()
    ))

    conn.commit()
    conn.close()