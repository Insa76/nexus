import uuid
import json

from core.database import get_connection


def save_pattern(

    pattern,
    solution,
    confidence=0.5,
    metadata=None
):

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO learned_patterns
        (
            id,
            pattern,
            solution,
            confidence,
            metadata
        )
        VALUES (%s,%s,%s,%s,%s)
    """, (
        str(uuid.uuid4()),
        pattern,
        solution,
        confidence,
        json.dumps(metadata)
        if metadata
        else None
    ))

    conn.commit()
    conn.close()


def load_patterns(limit=20):

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT *
        FROM learned_patterns
        ORDER BY confidence DESC
        LIMIT %s
    """, (limit,))

    rows = cur.fetchall()

    conn.close()

    return [dict(r) for r in rows]