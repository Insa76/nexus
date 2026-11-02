import json
from pathlib import Path
from workflows.engine import load_workflows, save_workflows

TEMPLATES_DIR = Path("workflows/templates")


def list_templates():

    return [f.stem for f in TEMPLATES_DIR.glob("*.json")]


def load_template(name):

    file = TEMPLATES_DIR / f"{name}.json"

    if not file.exists():
        return None

    return json.loads(file.read_text())


def import_template(name):

    tpl = load_template(name)

    if not tpl:
        return False

    current = load_workflows()

    merged = current + tpl

    save_workflows(merged)

    return True