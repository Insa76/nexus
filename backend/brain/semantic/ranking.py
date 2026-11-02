import json
import math

from core.database import get_connection
from brain.semantic.embedder import embed


# ==========================================================
# COSINE SIMILARITY
# ==========================================================

def cosine(a, b):
    dot = sum(x * y for x, y in zip(a, b))
    mag_a = math.sqrt(sum(x * x for x in a))
    mag_b = math.sqrt(sum(x * x for x in b))
    return dot / (mag_a * mag_b + 1e-8)


# ==========================================================
# SEARCH SIMILAR
# ==========================================================

def search_similar(user_id, query, limit=5):

    q_vec = embed(query)

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT id, content, embedding, confidence
        FROM semantic_vectors
        WHERE user_id = %s
    """, (user_id,))

    rows = cur.fetchall()
    conn.close()

    scored = []

    for row in rows:
        emb = json.loads(row[2])  # embedding guardado como JSON
        confidence = row[3] if row[3] else 1.0

        score = cosine(q_vec, emb) * confidence

        scored.append({
            "id": row[0],
            "content": row[1],
            "score": score
        })

    # ordenar por score
    scored.sort(key=lambda x: x["score"], reverse=True)

    return scored[:limit]