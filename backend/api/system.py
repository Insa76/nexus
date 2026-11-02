from fastapi import APIRouter
from core.metrics import metrics
from core.self_model import self_model
from core.database import get_connection

router = APIRouter()

@router.get("/system/health")
async def system_health():

    snapshot = self_model.snapshot()
    health = self_model.health_score(snapshot)

    return {
        "health_score": health,
        "error_rate": snapshot["error_rate"],
        "queue_size": snapshot["queue_size"],
        "open_circuits": snapshot["open_circuits"],
        "total_jobs": snapshot["total_jobs"]
    }

@router.get("/system/errors")
async def system_errors():

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT error, COUNT(*) as total
        FROM (
            SELECT json_extract(result,'$.error') as error
            FROM jobs
            WHERE status='error'
        )
        WHERE error IS NOT NULL
        GROUP BY error
        ORDER BY total DESC
        LIMIT 10
    """)

    rows = cur.fetchall()
    conn.close()

    errors = []

    for r in rows:
        errors.append({
            "error": r["error"],
            "count": r["total"]
        })

    return errors