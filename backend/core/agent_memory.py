import uuid
import json

from core.database import get_connection


def save_memory(

    agent,
    role,
    content,
    metadata=None
):

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO agent_memory
        (
            id,
            agent,
            role,
            content,
            metadata
        )
        VALUES (%s,%s,%s,%s,%s)
    """, (
        str(uuid.uuid4()),
        agent,
        role,
        content,
        json.dumps(metadata)
        if metadata
        else None
    ))

    conn.commit()
    conn.close()


def load_memory(
    agent,
    limit=10
):

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT *
        FROM agent_memory
        WHERE agent = %s
        ORDER BY created_at DESC
        LIMIT %s
    """, (
        agent,
        limit
    ))

    rows = cur.fetchall()

    conn.close()

    return [dict(r) for r in rows]