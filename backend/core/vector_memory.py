import uuid
import json

from core.database import get_connection

from core.embeddings import (
    fake_embedding,
    cosine_similarity
)


def save_vector_memory(

    agent,
    content,
    metadata=None
):

    embedding = fake_embedding(
        content
    )

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO vector_memory
        (
            id,
            agent,
            content,
            embedding,
            metadata
        )
        VALUES (%s,%s,%s,%s,%s)
    """, (
        str(uuid.uuid4()),
        agent,
        content,
        json.dumps(embedding),
        json.dumps(metadata)
        if metadata
        else None
    ))

    conn.commit()
    conn.close()


def search_memory(

    agent,
    query,
    limit=5
):

    query_embedding = fake_embedding(
        query
    )

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT *
        FROM vector_memory
        WHERE agent = %s
    """, (agent,))

    rows = cur.fetchall()

    conn.close()

    scored = []

    for row in rows:

        embedding = row["embedding"]

        if isinstance(embedding, str):
            embedding = json.loads(
                embedding
            )

        score = cosine_similarity(
            query_embedding,
            embedding
        )

        scored.append({
            "score": score,
            "memory": dict(row)
        })

    scored.sort(
        key=lambda x: x["score"],
        reverse=True
    )

    return scored[:limit]