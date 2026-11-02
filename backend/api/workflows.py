import uuid
import json

from fastapi import APIRouter, Depends

from auth.deps import get_current_user
from core.database import get_connection

router = APIRouter(prefix="/workflows")


# =========================
# SAVE WORKFLOW
# =========================
@router.post("/save")
def save_workflow(
    data: dict,
    user=Depends(get_current_user)
):

    conn = get_connection()
    cur = conn.cursor()

    workflow_id = str(uuid.uuid4())

    cur.execute("""
        INSERT INTO workflows
        (
            id,
            tenant_id,
            name,
            nodes,
            edges
        )
        VALUES (%s, %s, %s, %s, %s)
    """, (
        workflow_id,
        user["tenant_id"],
        data["name"],
        json.dumps(data["nodes"]),
        json.dumps(data["edges"])
    ))

    conn.commit()
    conn.close()

    return {
        "success": True,
        "workflow_id": workflow_id
    }


# =========================
# LIST WORKFLOWS
# =========================
@router.get("/")
def list_workflows(
    user=Depends(get_current_user)
):

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT *
        FROM workflows
        WHERE tenant_id = %s
        ORDER BY created_at DESC
    """, (user["tenant_id"],))

    rows = cur.fetchall()

    conn.close()

    return [dict(r) for r in rows]


# =========================
# LOAD WORKFLOW
# =========================
@router.get("/{workflow_id}")
def load_workflow(
    workflow_id: str,
    user=Depends(get_current_user)
):

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT *
        FROM workflows
        WHERE id = %s
        AND tenant_id = %s
    """, (
        workflow_id,
        user["tenant_id"]
    ))

    row = cur.fetchone()

    conn.close()

    if not row:
        return {"error": "Workflow not found"}

    workflow = dict(row)

    return {
        "id": workflow["id"],
        "name": workflow["name"],
        "nodes": workflow["nodes"],
        "edges": workflow["edges"]
    }