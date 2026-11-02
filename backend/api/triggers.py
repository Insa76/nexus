import uuid
import json

from fastapi import APIRouter, Depends

from auth.deps import get_current_user
from core.database import get_connection

router = APIRouter(prefix="/triggers")


# =========================
# CREATE
# =========================
@router.post("/")
def create_trigger(
    data: dict,
    user=Depends(get_current_user)
):

    conn = get_connection()
    cur = conn.cursor()

    trigger_id = str(uuid.uuid4())

    cur.execute("""
        INSERT INTO triggers
        (
            id,
            tenant_id,
            name,
            trigger_type,
            config,
            workflow_id
        )
        VALUES (%s,%s,%s,%s,%s,%s)
    """, (
        trigger_id,
        user["tenant_id"],
        data["name"],
        data["trigger_type"],
        json.dumps(data["config"]),
        data["workflow_id"]
    ))

    conn.commit()
    conn.close()

    return {
        "success": True
    }


# =========================
# LIST
# =========================
@router.get("/")
def list_triggers(
    user=Depends(get_current_user)
):

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT *
        FROM triggers
        WHERE tenant_id = %s
        ORDER BY created_at DESC
    """, (user["tenant_id"],))

    rows = cur.fetchall()

    conn.close()

    return [dict(r) for r in rows]