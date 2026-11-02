from fastapi import APIRouter, Depends, HTTPException
import psutil
from pathlib import Path

from plugins.loader import PLUGINS
from learning.suggest import get_suggestions
from brain.personal_memory.recall import recall
from auth.deps import get_current_user  # 🔥 IMPORTANTE


router = APIRouter(prefix="/dashboard")


# 🔹 estado sistema (GLOBAL)
@router.get("/stats")
def stats():

    return {
        "cpu": psutil.cpu_percent(),
        "ram": psutil.virtual_memory().percent,
        "processes": len(psutil.pids())
    }


# 🔹 plugins (GLOBAL)
@router.get("/plugins")
def plugins():
    return {"plugins": list(PLUGINS.keys())}


# 🔹 logs (GLOBAL)
@router.get("/logs")
def logs():

    file = Path("nexus_logs.txt")

    if not file.exists():
        return {"logs": []}

    lines = file.read_text(encoding="utf-8").splitlines()

    return {"logs": lines[-50:]}


# 🔹 suggestions (POR USUARIO / TENANT)
@router.get("/suggestions")
def suggestions(user=Depends(get_current_user)):

    if not user:
     raise HTTPException(status_code=401, detail="Unauthorized")

    tenant_id = user["tenant_id"]

    # 👉 si después querés, podés filtrar por tenant dentro de get_suggestions
    return {
        "tenant": tenant_id,
        "suggestions": get_suggestions()
    }


# 🔹 memory (CRÍTICO → SIEMPRE TENANT)
@router.get("/memory")
def memory(user=Depends(get_current_user)):

    tenant_id = user["tenant_id"]

    return {
        "tenant": tenant_id,
        "memory": recall("todo", 10)  # 🔥 ideal: después filtrar por tenant
    }