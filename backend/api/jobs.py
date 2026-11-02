from fastapi import APIRouter, Depends, HTTPException
import jobs.manager as manager_module
from core.database import get_connection
from auth.deps import get_current_user

router = APIRouter(prefix="/jobs")


# =========================
# RUN JOB
# =========================
@router.post("/run")
async def run(data: dict, user=Depends(get_current_user)):

    tenant_id = user["tenant_id"]

    try:

        # =========================
        # 1. RUN DESDE BUILDER
        # =========================
        if "nodes" in data:

          workflow = {
           "nodes": data["nodes"],
           "edges": data.get("edges", [])
         }

          job_id = await manager_module.manager.create_job(
           workflow,
           tenant_id
         )

          return {"job_id": job_id}

        # =========================
        # 2. RUN POR NOMBRE (DB)
        # =========================
        elif "name" in data:

            job_id = await manager_module.manager.create_job(
                data["name"],
                tenant_id
            )

            return {"job_id": job_id}

        else:
            raise Exception("Payload inválido")

    except Exception as e:
        return {"error": str(e)}


# =========================
# LIST JOBS (FILTRADO)
# =========================
@router.get("/")
def list_jobs(user=Depends(get_current_user)):

    tenant_id = user["tenant_id"]

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT *
        FROM jobs
        WHERE tenant_id = %s
        ORDER BY updated_at DESC
    """, (tenant_id,))

    rows = cur.fetchall()
    conn.close()

    return [dict(r) for r in rows]


# =========================
# RETRY JOB (VALIDAR TENANT)
# =========================
@router.post("/retry/{job_id}")
async def retry(job_id: str, user=Depends(get_current_user)):

    tenant_id = user["tenant_id"]

    conn = get_connection()
    cur = conn.cursor()

    # verificar que el job pertenece al tenant
    cur.execute("""
        SELECT id
        FROM jobs
        WHERE id = %s AND tenant_id = %s
    """, (job_id, tenant_id))

    job = cur.fetchone()
    conn.close()

    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    return await manager_module.manager.retry_job(job_id)


# =========================
# JOB STEPS (FILTRADO)
# =========================
@router.get("/{job_id}/steps")
async def job_steps(job_id: str, user=Depends(get_current_user)):

    tenant_id = user["tenant_id"]

    conn = get_connection()
    cur = conn.cursor()

    # validar tenant
    cur.execute("""
        SELECT id
        FROM jobs
        WHERE id = %s AND tenant_id = %s
    """, (job_id, tenant_id))

    job = cur.fetchone()

    if not job:
        conn.close()
        raise HTTPException(status_code=404, detail="Job not found")

    # traer steps
    cur.execute("""
        SELECT step, status, result, timestamp
        FROM job_steps
        WHERE job_id = %s
        ORDER BY timestamp ASC
    """, (job_id,))

    rows = cur.fetchall()
    conn.close()

    return [
        {
            "step": r["step"],
            "status": r["status"],
            "result": r["result"],
            "timestamp": str(r["timestamp"])
        }
        for r in rows
    ]