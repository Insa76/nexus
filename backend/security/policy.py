# acciones seguras
SAFE = {
    "open_app",
    "list_files",
    "list_processes"
}

# acciones que requieren confirmación
CONFIRM = {
    "delete_file",
    "move_files",
    "run_cmd",
    "close_active_app"
}

# sandbox (solo estas rutas permitidas)
ALLOWED_PATHS = [
    "C:\\Users",
    "."
]


def is_path_allowed(path):

    for base in ALLOWED_PATHS:
        if path.startswith(base):
            return True

    return False


def requires_confirm(action):
    return action in CONFIRM


def is_safe(action):
    return action in SAFE
