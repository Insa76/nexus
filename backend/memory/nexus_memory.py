import json
from pathlib import Path

MEMORY_FILE = Path("nexus_memory.json")


def load_memory():

    if not MEMORY_FILE.exists():
        return {"workflows":[], "errors":[], "preferences":{}}

    try:
        return json.loads(MEMORY_FILE.read_text())
    except:
        return {"workflows":[], "errors":[], "preferences":{}}


def save_memory(memory):

    MEMORY_FILE.write_text(json.dumps(memory, indent=2))

def remember_success(workflow_name):

    memory = load_memory()

    memory["workflows"].append({
        "workflow":workflow_name
    })

    save_memory(memory)
    
def remember_error(workflow_name, error):

    memory = load_memory()

    memory["errors"].append({
        "workflow":workflow_name,
        "error":error
    })

    save_memory(memory)        