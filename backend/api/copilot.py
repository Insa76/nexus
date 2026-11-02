from fastapi import APIRouter
from copilot.copilot_engine import copilot
from workflows.repository import save_workflow_version
from workflows.validator import validate_workflow
from copilot.debugger import debugger
from copilot.fixer import fixer

router = APIRouter(prefix="/copilot", tags=["copilot"])


@router.post("/generate")
def generate(data: dict):

    prompt = data.get("prompt")

    workflow = copilot.interpret(prompt)
    workflow = validate_workflow(workflow)

    if not workflow:
        return {
            "ok": False,
            "message": "No pude interpretar la instrucción."
        }

    save_workflow_version(
        workflow["name"],
        workflow["trigger"],
        workflow["steps"],
        "default",
        "main"
    )

    return {
        "ok": True,
        "workflow": workflow
    }

@router.get("/debug-last")
def debug_last():

    result = debugger.analyze_last_failure()

    return result

@router.get("/fix-last")
def fix_last():

    result = fixer.propose_fix()

    return result