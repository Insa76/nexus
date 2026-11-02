from fastapi import APIRouter, Depends
from core.database import get_connection
from auth.deps import get_current_user

router = APIRouter(prefix="/dlq")


@router.get("/")
def list_dead_jobs(user=Depends(get_current_user)):

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
    SELECT * FROM dead_jobs
    WHERE tenant_id=%s AND workspace_id=%s
    ORDER BY created_at DESC
    """, (
        user["tenant_id"],
        user["workspace_id"]
    ))

    rows = cur.fetchall()
    conn.close()

    return rows

@router.post("/retry/{dead_id}")
def retry_dead(dead_id: str, user=Depends(get_current_user)):

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT * FROM dead_jobs WHERE id=%s", (dead_id,))
    job = cur.fetchone()

    if not job:
        return {"error": "not found"}

    from jobs.manager import manager

    import asyncio
    asyncio.create_task(
        manager.create_job(job["workflow"],
                           job["tenant_id"],
                           job["workspace_id"])
    )

    return {"status": "requeued"}