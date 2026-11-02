from fastapi import APIRouter
import json
from pathlib import Path
from packs.loader import install_pack

router = APIRouter(prefix="/setup")

FILE = Path("config/state.json")


@router.get("/")
def status():
    return json.loads(FILE.read_text())


@router.post("/install")
def install(data: dict):

    install_pack(data["slug"])

    FILE.write_text(json.dumps({"installed": True}))

    return {"ok": True}