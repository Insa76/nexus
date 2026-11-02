import json
from pathlib import Path

FILE = Path("nexus_learning.json")


def track(action, value):

    # Crear archivo si no existe
    if not FILE.exists():
        FILE.write_text("{}")

    try:
        content = FILE.read_text().strip()

        if not content:
            data = {}
        else:
            data = json.loads(content)

    except Exception:
        # Si está corrupto lo reseteamos
        data = {}

    # Inicializar contador
    if action not in data:
        data[action] = 0

    data[action] += 1

    FILE.write_text(json.dumps(data, indent=2))