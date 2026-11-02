from fastapi import APIRouter
from pydantic import BaseModel
from fastapi import Request

from brain.agent import ask_nexus
from actions.system_actions import execute_action
from memory.indexer import index_folder

router = APIRouter()


class Query(BaseModel):
    message: str


@router.post("/ask")
def ask(q: Query, request: Request):
    result = ask_nexus(q.message)

    # 🔥 acción simple
    if result.get("action"):
        output = execute_action(result["action"], result.get("value"), user)
        return {"type": "action", "result": output}

    # 🔥 texto normal / planner / fallback
    return {
        "type": "text",
        "result": result.get("response", str(result))
    }


@router.post("/index")
def index(data: dict):
    folder = data.get("folder")
    index_folder(folder)
    return {"status": "ok"}
