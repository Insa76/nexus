from fastapi import APIRouter, HTTPException

from brain.ai_planner import generate_workflow
from workflows.validator import validate_workflow
from workflows.repository import save_workflow_version

router = APIRouter(prefix="/ai", tags=["AI"])


@router.post("/workflow")
async def ai_workflow(data: dict):

    task = data.get("task")

    if not task:
        raise HTTPException(
            status_code=400,
            detail="task requerido"
        )

    try:

        # 1️⃣ generar workflow con IA
        wf = generate_workflow(task)

        # 2️⃣ validar estructura
        wf = validate_workflow(wf)

        # 3️⃣ guardar en DB
        save_workflow_version(
            wf["name"],
            wf.get("trigger", "manual"),
            wf["steps"]
        )

        return {
            "ok": True,
            "workflow": wf
        }

    except Exception as e:

        return {
            "ok": False,
            "error": str(e)
        }