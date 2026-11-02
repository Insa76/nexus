import os
import shutil
from pathlib import Path


def register(registry):

    registry["list_files"] = list_files
    registry["delete_file"] = delete_file
    registry["copy_file"] = copy_file


def list_files(path):
    return "\n".join(os.listdir(path))


def delete_file(path):
    os.remove(path)
    return f"Eliminado {path}"


def copy_file(data):
    shutil.copy(data["src"], data["dst"])
    return "Archivo copiado"
