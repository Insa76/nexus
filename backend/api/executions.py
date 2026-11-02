from fastapi import APIRouter, Depends

from auth.deps import get_current_user
from core.database import get_connection

router = APIRouter(prefix="/executions")


# =========================
# LIST EXECUTIONS
# =========================
@router.get("/{job_id}")
def get_executions(
    job_id: str,
    user=Depends(get_current_user)
):

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT *
        FROM workflow_executions
        WHERE job_id = %s
        ORDER BY created_at ASC
    """, (job_id,))

    rows = cur.fetchall()

    conn.close()

    return [dict(r) for r in rows]