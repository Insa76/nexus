import json
from datetime import datetime, timezone

from core.database import get_connection
from brain.semantic.embedder import embed


# ==========================================================
# SAVE VECTOR MEMORY
# ==========================================================

def save_vector_memory(user_id, content):

    vec = embed(content)

    conn = get_connection()
    cur = conn.cursor()

    now = datetime.now(timezone.utc)

    cur.execute("""
        INSERT INTO semantic_vectors
        (user_id, content, embedding, confidence, created_at, last_used)
        VALUES (%s, %s, %s, %s, %s, %s)
    """, (
        user_id,
        content,
        json.dumps(vec),
        0.6,
        now,
        now
    ))

    conn.commit()
    conn.close()