from fastapi import APIRouter
import uuid
from core.database import get_connection

router = APIRouter(prefix="/scheduler")


@router.get("/")
def list_schedules():

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT * FROM schedules")
    rows = cur.fetchall()
    conn.close()

    return rows


@router.post("/create")
def create(data: dict):

    schedule_id = str(uuid.uuid4())

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
    INSERT INTO schedules (id, workflow, type, expression, enabled)
    VALUES (%s, %s, %s, %s, 1)
    """, (
        schedule_id,
        data["workflow"],
        data["type"],
        data["expression"]
    ))

    conn.commit()
    conn.close()

    return {"id": schedule_id}