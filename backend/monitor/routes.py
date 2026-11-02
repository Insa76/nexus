from fastapi import APIRouter
from core.metrics import metrics
from core.database import get_connection
import psutil
import time

router = APIRouter(prefix="/monitor")


@router.get("/health")
def health():

    try:
        conn = get_connection()
        conn.execute("SELECT 1")
        conn.close()
        db_ok = True
    except:
        db_ok = False

    return {
        "status": "ok" if db_ok else "degraded",
        "database": db_ok,
        "cpu_percent": psutil.cpu_percent(),
        "memory_percent": psutil.virtual_memory().percent
    }


@router.get("/metrics")
def get_metrics():
    return metrics.snapshot()