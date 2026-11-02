from fastapi import APIRouter, HTTPException, Depends
from typing import List

from workflows.engine import run_workflow
from workflows.repository import (
    load_workflows,
    save_workflow_version
)
from workflows.schema import WorkflowModel
from workflows.ai_generator import generate_workflow 
from auth.deps import get_current_user
from audit.service import log_event


router = APIRouter(prefix="/workflows", tags=["workflows"])


# ==========================================================
# LIST WORKFLOWS
# ==========================================================

@router.get("/")
def list_workflows(user=Depends(get_current_user)):

    tenant_id = user["tenant_id"]
    workspace_id = user.get("workspace_id", "main")  # fallback seguro

    return load_workflows(
        tenant_id=tenant_id,
        workspace_id=workspace_id
    )


# ==========================================================
# SAVE WORKFLOW (VERSIONADO REAL)
# ==========================================================

@router.post("/save")
def save(data: dict, user=Depends(get_current_user)):

    tenant_id = user["tenant_id"]
    workspace_id = user.get("workspace_id", "main")

    version = save_workflow_version(
        name=data["name"],
        trigger=data["trigger"],
        steps=data["steps"],
        tenant_id=tenant_id,
        workspace_id=workspace_id
    )

    log_event(
        user,
        action="workflow_saved",
        entity="workflow",
        entity_id=data["name"],
        metadata={
            "version": version,
            "steps_count": len(data["steps"])
        }
    )

    return {"ok": True, "version": version}


# ==========================================================
# RUN WORKFLOW
# ==========================================================

@router.post("/run")
async def run(data: dict, user=Depends(get_current_user)):

    # 🔥 IMPORTANTE: el engine debe respetar tenant internamente
    result = await run_workflow(
        name=data["name"],
        user=user
    )

    return {"result": result}


# ==========================================================
# GENERATE WORKFLOW (IA)
# ==========================================================

@router.post("/generate")
def generate(data: dict, user=Depends(get_current_user)):  # 🔒 protegido

    raw = generate_workflow(data["prompt"])

    if "error" in raw:
        raise HTTPException(status_code=400, detail=raw["error"])

    try:
        validated = WorkflowModel(**raw)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    return validated.dict()


# ==========================================================
# LIST PACKS (placeholder)
# ==========================================================

@router.get("/packs")
def list_packs(user=Depends(get_current_user)):
    return []