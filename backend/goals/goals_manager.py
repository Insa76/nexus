import uuid
from datetime import datetime
from core.database import get_connection


def create_goal(goal):

    goal_id = str(uuid.uuid4())

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO goals
        (id, goal, status, created_at)
        VALUES (%s, %s, %s, %s)
    """, (
        goal_id,
        goal,
        "active",
        datetime.utcnow()
    ))

    conn.commit()
    conn.close()

    return goal_id


def list_goals():

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT id, goal, status
        FROM goals
    """)

    rows = cur.fetchall()
    conn.close()

    return [
        {
            "id": r["id"],
            "goal": r["goal"],
            "status": r["status"]
        }
        for r in rows
    ]