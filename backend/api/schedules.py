from fastapi import APIRouter, HTTPException, Depends
from core.database import get_connection
from datetime import datetime
from auth.deps import get_current_user

router = APIRouter(prefix="/schedules", tags=["schedules"])


# =========================
# GET ALL (FILTRADO POR TENANT)
# =========================
@router.get("/")
def list_schedules(user=Depends(get_current_user)):

    tenant_id = user["tenant_id"]

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT id, name, workflow, type, expression, enabled, last_run
        FROM schedules
        WHERE tenant_id = %s
        ORDER BY id DESC
    """, (tenant_id,))

    rows = cur.fetchall()
    conn.close()

    return [dict(row) for row in rows]


# =========================
# CREATE (CON TENANT)
# =========================
@router.post("/")
def create_schedule(data: dict, user=Depends(get_current_user)):

    tenant_id = user["tenant_id"]

    required = ["name", "workflow", "type", "expression"]

    for r in required:
        if r not in data:
            raise HTTPException(400, f"Falta campo: {r}")

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO schedules
        (name, workflow, type, expression, enabled, last_run, tenant_id)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        RETURNING id
    """, (
        data["name"],
        data["workflow"],
        data["type"],       # interval / cron
        data["expression"],
        True,
        None,
        tenant_id
    ))

    new_id = cur.fetchone()[0]

    conn.commit()
    conn.close()

    return {"ok": True, "id": new_id}


# =========================
# TOGGLE ENABLE (SEGURIDAD TENANT)
# =========================
@router.post("/{schedule_id}/toggle")
def toggle_schedule(schedule_id: int, user=Depends(get_current_user)):

    tenant_id = user["tenant_id"]

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        UPDATE schedules
        SET enabled = NOT enabled
        WHERE id = %s AND tenant_id = %s
        RETURNING enabled
    """, (schedule_id, tenant_id))

    row = cur.fetchone()

    conn.commit()
    conn.close()

    if not row:
        raise HTTPException(404, "Schedule no encontrado")

    return {"enabled": row[0]}


# =========================
# DELETE (SEGURIDAD TENANT)
# =========================
@router.delete("/{schedule_id}")
def delete_schedule(schedule_id: int, user=Depends(get_current_user)):

    tenant_id = user["tenant_id"]

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        DELETE FROM schedules
        WHERE id = %s AND tenant_id = %s
    """, (schedule_id, tenant_id))

    conn.commit()
    conn.close()

    return {"ok": True}