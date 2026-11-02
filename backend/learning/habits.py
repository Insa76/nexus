import json
from pathlib import Path

FILE = Path("nexus_learning.json")


def detect_habits():

    if not FILE.exists():
        return []

    try:
        raw = FILE.read_text().strip()

        if not raw:
            return []

        data = json.loads(raw)

        if not isinstance(data, dict):
            return []

    except Exception:
        return []

    habits = []

    for action, times in data.items():
        if times >= 5:
            habits.append({
                "action": action,
                "count": times
            })

    # ordenar por frecuencia
    habits.sort(key=lambda x: x["count"], reverse=True)

    return habits