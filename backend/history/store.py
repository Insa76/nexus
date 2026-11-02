import json
from pathlib import Path

FILE = Path("nexus_history.json")


def load_history():
    if FILE.exists():
        return json.loads(FILE.read_text(encoding="utf-8"))
    return []


def save_history(history):
    FILE.write_text(json.dumps(history[-50:], indent=2), encoding="utf-8")
