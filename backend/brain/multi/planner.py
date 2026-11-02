import ollama
import json

SYSTEM = """
Convertí la orden del usuario en un plan JSON.

Formato:
{
  "steps": [
    {"action": "open_app", "value": "notepad"}
  ]
}

Solo JSON.
"""


def plan_task(message):

    res = ollama.chat(
        model="llama3",
        messages=[
            {"role": "system", "content": SYSTEM},
            {"role": "user", "content": message}
        ]
    )

    try:
        return json.loads(res["message"]["content"])
    except:
        return {"steps": []}
