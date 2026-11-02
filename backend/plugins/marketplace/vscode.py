import subprocess


def register(registry):
    registry["open_project"] = open_project


def open_project(path):

    subprocess.Popen(["code", path])

    return f"Proyecto abierto en VSCode: {path}"
