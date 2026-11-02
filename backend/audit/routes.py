from fastapi import APIRouter, Depends
from core.database import get_connection
from auth.deps import get_current_user

router = APIRouter(prefix="/audit")


@router.get("/")
def get_logs(user=Depends(get_current_user)):

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
    SELECT * FROM audit_logs
    WHERE tenant_id=%s AND workspace_id=%s
    ORDER BY created_at DESC
    LIMIT 200
    """, (
        user["tenant_id"],
        user["workspace_id"]
    ))

    rows = cur.fetchall()
    conn.close()

    return rows