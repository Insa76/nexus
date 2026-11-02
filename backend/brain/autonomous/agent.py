import ollama
import json

SYSTEM = """
Sos un agente autónomo.

Objetivo:
Dividí la meta del usuario en pasos pequeños ejecutables.

Formato:
{
  "steps":[
    {"action":"create_folder","value":"report"},
    {"action":"open_app","value":"notepad"}
  ],
  "done": false
}

Si ya terminaste:
{"done": true}

Solo JSON.
"""


def next_step(goal, history):

    res = ollama.chat(
        model="llama3",
        messages=[
            {"role": "system", "content": SYSTEM},
            {"role": "user", "content": f"Objetivo: {goal}\nHistorial:\n{history}"}
        ]
    )

    try:
        return json.loads(res["message"]["content"])
    except:
        return {"done": True}
