import psutil
import os
import platform

# =========================
# Windows-only dependency
# =========================

if platform.system() == "Windows":
    try:
        import pygetwindow as gw
    except Exception:
        gw = None
else:
    gw = None


# =========================
# ACTIVE WINDOW
# =========================

def active_window():

    if gw is None:
        return "unsupported_os"

    try:
        win = gw.getActiveWindow()
        return win.title if win else "unknown"
    except Exception:
        return "unknown"


# =========================
# RUNNING PROCESSES
# =========================

def running_processes(limit=10):

    procs = []

    for p in psutil.process_iter(['name', 'cpu_percent']):
        try:
            procs.append((p.info['name'], p.info['cpu_percent']))
        except Exception:
            pass

    procs.sort(key=lambda x: x[1], reverse=True)

    return [p[0] for p in procs[:limit]]


# =========================
# CURRENT FOLDER
# =========================

def current_folder():
    return os.getcwd()


# =========================
# GLOBAL CONTEXT
# =========================

def get_context():

    processes = ", ".join(running_processes())

    return f"""
Ventana activa: {active_window()}
Carpeta actual: {current_folder()}
Procesos principales: {processes}
"""