from datetime import datetime, timedelta
from core.database import get_connection


def apply_decay():

    conn = get_connection()
    cur = conn.cursor()

    threshold = datetime.utcnow() - timedelta(days=30)

    cur.execute("""
        UPDATE semantic_vectors
        SET confidence = confidence * 0.9
        WHERE last_used < %s
    """, (threshold,))

    conn.commit()
    conn.close()