from datetime import datetime, timezone

from core.database import get_connection


def save_semantic(user_id, key, value, confidence=0.6):

    conn = get_connection()
    cur = conn.cursor()

    # 🔍 Buscar existente
    cur.execute("""
        SELECT id, confidence
        FROM semantic_memory
        WHERE user_id = %s AND key = %s
    """, (user_id, key))

    row = cur.fetchone()

    now = datetime.now(timezone.utc)

    if row:
        semantic_id = row[0]
        current_conf = row[1]

        new_conf = min(1.0, current_conf + 0.1)

        cur.execute("""
            UPDATE semantic_memory
            SET value = %s,
                confidence = %s,
                updated_at = %s
            WHERE id = %s
        """, (value, new_conf, now, semantic_id))

    else:
        cur.execute("""
            INSERT INTO semantic_memory
            (user_id, key, value, confidence, created_at, updated_at)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (user_id, key, value, confidence, now, now))

    conn.commit()
    conn.close()