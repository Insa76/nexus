import os
import shutil
from pathlib import Path

from actions.registry import register_action


def create_folder(value):

    Path(value).mkdir(parents=True, exist_ok=True)

    return f"Carpeta creada: {value}"


def list_dir(value):

    files = os.listdir(value or ".")

    return "\n".join(files)


def move_files(value):

    ext = value["ext"]
    to = value["to"]

    Path(to).mkdir(exist_ok=True)

    moved = 0

    for f in os.listdir("."):
        if f.lower().endswith(ext):
            shutil.move(f, os.path.join(to, f))
            moved += 1

    return f"{moved} archivos movidos a {to}"


register_action("create_folder", create_folder)
register_action("list_dir", list_dir)
register_action("move_files", move_files)