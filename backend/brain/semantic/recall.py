from core.database import get_connection


def recall_semantic(user_id):

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT key, value, confidence
        FROM semantic_memory
        WHERE user_id = %s
        ORDER BY confidence DESC
        LIMIT 20
    """, (user_id,))

    rows = cur.fetchall()
    conn.close()

    return rows