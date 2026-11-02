from fastapi import APIRouter
from plugin_manager.registry import REGISTRY
from plugin_manager.installer import install_plugin, remove_plugin
from plugin_manager.loader import load_installed

router = APIRouter(prefix="/market")


@router.get("/")
def list_plugins():
    return {"plugins": REGISTRY}


@router.post("/install")
def install(data: dict):
    msg = install_plugin(data["file"])
    load_installed()
    return {"status": msg}


@router.post("/remove")
def remove(data: dict):
    msg = remove_plugin(data["file"])
    load_installed()
    return {"status": msg}
