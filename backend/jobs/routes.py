from fastapi import APIRouter, Depends, HTTPException
from jobs.manager import manager
from auth.deps import get_current_user
from audit.service import log_event
from core.database import get_connection

router = APIRouter(prefix="/jobs")


# ======================================================
# RUN JOB (🔥 SOPORTA IA + WORKFLOWS)
# ======================================================

@router.post("/run")
async def run(data: dict, user=Depends(get_current_user)):

    tenant_id = user["tenant_id"]
    workspace_id = user["workspace_id"]

    # =========================
    # 🔥 CASO 1: WORKFLOW POR NOMBRE
    # =========================
    if data.get("name"):

        job_id = await manager.create_job(
            data["name"],
            tenant_id,
            workspace_id
        )

        log_event(
            user,
            action="job_created",
            entity="workflow",
            entity_id=data["name"],
            metadata={"job_id": job_id}
        )

        return {"job_id": job_id}

    # =========================
    # 🔥 CASO 2: STEPS (AI BUILDER)
    # =========================
    if data.get("steps"):

        job_id = await manager.create_job_from_steps(
            data["steps"],
            tenant_id,
            workspace_id
        )

        log_event(
            user,
            action="job_created",
            entity="workflow_ai",
            entity_id="ai_generated",
            metadata={"job_id": job_id}
        )

        return {"job_id": job_id}

    # =========================
    # ❌ ERROR
    # =========================
    raise HTTPException(
        status_code=400,
        detail="Debe enviar 'name' o 'steps'"
    )


# ======================================================
# LIST JOBS
# ======================================================

@router.get("/")
def list_jobs():
    return manager.list_jobs()


# ======================================================
# JOB STEPS
# ======================================================

@router.get("/{job_id}/steps")
def get_job_steps(job_id: str):

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT *
        FROM step_executions
        WHERE job_id=%s
        ORDER BY started_at
    """, (job_id,))

    rows = cur.fetchall()
    conn.close()

    return rows