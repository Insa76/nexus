import json
import ollama
from actions.system_actions import execute_action


SYSTEM = """
Sos Nexus Planner.

Convertí la orden del usuario en un PLAN JSON.

Formato:
{
  "steps": [
    {"action": "create_folder", "value": "PDF"},
    {"action": "move_files", "value": {"ext": ".pdf", "to": "PDF"}}
  ]
}

Acciones disponibles:
- open_app
- open_file
- create_folder
- move_files
- run_cmd

Solo devolver JSON.
"""


def run_plan(user_message: str):

    res = ollama.chat(
        model="llama3",
        messages=[
            {"role": "system", "content": SYSTEM},
            {"role": "user", "content": user_message}
        ]
    )

    content = res["message"]["content"]

    try:
        plan = json.loads(content)
    except:
        return "No pude generar un plan."

    outputs = []

    for step in plan.get("steps", []):
        out = execute_action(step["action"], step["value"])
        outputs.append(out)

    return "\n".join(outputs)
