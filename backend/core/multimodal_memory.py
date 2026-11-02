import uuid
import json

from core.database import get_connection


def save_multimodal_memory(

    agent,
    image_path,
    ocr_text,
    objects,
    metadata=None
):

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO multimodal_memory
        (
            id,
            agent,
            image_path,
            ocr_text,
            objects,
            metadata
        )
        VALUES (%s,%s,%s,%s,%s,%s)
    """, (
        str(uuid.uuid4()),
        agent,
        image_path,
        ocr_text,
        json.dumps(objects),
        json.dumps(metadata)
        if metadata
        else None
    ))

    conn.commit()
    conn.close()


def load_recent_memories(
    agent,
    limit=10
):

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT *
        FROM multimodal_memory
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