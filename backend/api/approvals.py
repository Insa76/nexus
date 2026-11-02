from fastapi import APIRouter

import jobs.manager as manager_module

router = APIRouter(prefix="/approvals")


@router.post("/{job_id}")
async def approve(job_id: str):

    await manager_module.manager.resume_job(
        job_id
    )

    return {
        "success": True
    }