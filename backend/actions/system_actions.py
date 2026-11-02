import os
import subprocess
import shutil
import time
import webbrowser
from pathlib import Path
import asyncio

import psutil

from plugins.loader import run_plugin, load_plugins
from security.policy import requires_confirm, is_path_allowed
from security.logger import log
from learning.tracker import track

from integrations.http_client import http_request
from integrations.slack import send_slack
from integrations.email import send_email

from actions.registry import get_action


# ==================================================
# 🔥 CARGAR PLUGINS
# ==================================================

load_plugins()


# ==================================================
# 🔥 ALIASES
# ==================================================

ALIASES = {
    "open_browser": "open_app",
    "launch_app": "open_app",
    "start_app": "open_app",
    "delete": "delete_file",
    "remove_file": "delete_file",
    "copy": "copy_file",
    "move": "move_files",
}


def normalize(action: str):
    return ALIASES.get(action, action)


# ==================================================
# 🔐 ROLES
# ==================================================

def check_role(user, action):

    role = user.get("role")

    if role == "admin":
        return True

    if role == "staff" and action in [
        "delete_file", "run_cmd", "kill_process"
    ]:
        return False

    if role == "viewer":
        return False

    return True


# ==================================================
# 🔐 SEGURIDAD
# ==================================================

def confirm_if_needed(action, value, auto=True):

    if auto:
        return True

    try:
        resp = input(f"Confirmar acción {action}? (y/n): ")
        return resp.lower() == "y"
    except:
        return False


def sandbox_check(value):
    if isinstance(value, str) and ("\\" in value or "/" in value):
        if not is_path_allowed(value):
            return False
    return True


# ==================================================
# 🔥 MAIN EXECUTOR (ASYNC)
# ==================================================

async def execute_action(action, value, user=None):

    if user is None:
        user = {"role": "admin"}

    action = normalize(action)

    if not check_role(user, action):
        return "⛔ Permiso denegado"

    if not sandbox_check(value):
        return "⛔ Ruta no permitida por seguridad"

    if not confirm_if_needed(action, value):
        return "Acción cancelada"

    result = None

    plugin = get_action(action)

    if plugin:
      result = plugin(value)
      return result

    # ==================================================
    # 📦 APPS
    # ==================================================

    if action == "open_app":

        shortcuts = {
            "chrome": r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            "edge": r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
            "notepad": "notepad",
            "calc": "calc",
        }

        value = shortcuts.get(str(value).lower(), value)
        subprocess.Popen(value)
        result = f"Abriendo {value}"

    elif action == "open_url":

        webbrowser.open(value)
        result = f"Abriendo URL {value}"

    # ==================================================
    # 📁 FILESYSTEM
    # ==================================================

    elif action == "list_dir":
        files = os.listdir(value or ".")
        result = "\n".join(files)

    elif action == "read_file":
        result = Path(value).read_text(encoding="utf-8")

    elif action == "write_file":
        Path(value["path"]).write_text(value["content"], encoding="utf-8")
        result = f"Archivo guardado: {value['path']}"

    elif action == "delete_file":
        os.remove(value)
        result = f"Archivo eliminado: {value}"

    elif action == "copy_file":
        shutil.copy(value["src"], value["dst"])
        result = "Archivo copiado"

    elif action == "rename_file":
        os.rename(value["src"], value["dst"])
        result = "Archivo renombrado"

    elif action == "create_folder":
        Path(value).mkdir(parents=True, exist_ok=True)
        result = f"Carpeta creada: {value}"

    elif action == "move_files":

        ext = value["ext"]
        to = value["to"]

        Path(to).mkdir(exist_ok=True)

        moved = 0

        for f in os.listdir("."):
            if f.lower().endswith(ext):
                shutil.move(f, os.path.join(to, f))
                moved += 1

        result = f"{moved} archivos movidos a {to}"

    # ==================================================
    # 🌐 INTEGRACIONES EXTERNAS
    # ==================================================

    elif action == "http_request":

        result = await http_request(
            value["method"],
            value["url"],
            value.get("headers"),
            value.get("body"),
            value.get("timeout", 10)
        )

    elif action == "send_slack":

        result = await send_slack(
            value["webhook_url"],
            value["message"]
        )

    elif action == "send_email":

        result = await send_email(
            value["smtp_host"],
            value["smtp_port"],
            value["username"],
            value["password"],
            value["to"],
            value["subject"],
            value["body"]
        )

    # ==================================================
    # 🖥 SISTEMA
    # ==================================================

    elif action == "list_processes":
        names = [p.info['name'] for p in psutil.process_iter(['name'])]
        result = "\n".join(names)

    elif action == "kill_process":

        for p in psutil.process_iter(['name']):
            if p.info['name'].lower() == value.lower():
                p.kill()
                result = f"{value} finalizado"
                break
        else:
            result = "Proceso no encontrado"

    elif action == "get_time":
        from datetime import datetime
        result = datetime.now().strftime("%H:%M:%S")

    elif action == "system_info":

        result = f"""
        OS: {os.name}
        CPU: {psutil.cpu_percent()}%
        RAM: {psutil.virtual_memory().percent}%
        """

    elif action == "sleep":
        await asyncio.sleep(float(value))
        result = f"Esperado {value}s"

    # ==================================================
    # 💻 SHELL
    # ==================================================

    elif action == "run_cmd":
        result = subprocess.getoutput(value)

    # ==================================================
    # 🔌 PLUGINS
    # ==================================================

    else:

        plugin_result = run_plugin(action, value)

        if plugin_result is not None:
            result = plugin_result
        else:
            result = f"Acción no reconocida: {action}"

    # ==================================================
    # 🔥 LOG + TRACK
    # ==================================================

    log(action, result)
    track(action, value)

    return result