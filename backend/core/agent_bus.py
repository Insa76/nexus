import uuid
import json

from core.database import get_connection


def send_message(

    sender,
    receiver,
    message,
    metadata=None
):

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO agent_messages
        (
            id,
            sender,
            receiver,
            message,
            metadata
        )
        VALUES (%s,%s,%s,%s,%s)
    """, (
        str(uuid.uuid4()),
        sender,
        receiver,
        message,
        json.dumps(metadata)
        if metadata
        else None
    ))

    conn.commit()
    conn.close()


def get_messages(
    receiver,
    limit=20
):

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT *
        FROM agent_messages
        WHERE receiver = %s
        ORDER BY created_at DESC
        LIMIT %s
    """, (
        receiver,
        limit
    ))

    rows = cur.fetchall()

    conn.close()

    return [dict(r) for r in rows]