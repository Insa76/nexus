import json
import requests
import re


OLLAMA_URL = "http://localhost:11434/api/generate"


SYSTEM_PROMPT = """
Eres un generador de workflows para Nexus Automation Engine.

Devuelve SOLO JSON válido.

Formato requerido:

{
 "name": "workflow_name",
 "trigger": "manual",
 "steps": [
   {
     "type": "action",
     "action": "action_name",
     "value": "value"
   }
 ]
}

Acciones disponibles y su formato:

create_folder

{
 "type": "action",
 "action": "create_folder",
 "value": "FOLDER_NAME"
}

move_files

{
 "type": "action",
 "action": "move_files",
 "value": {
   "ext": ".pdf",
   "to": "PDF"
 }
}

list_dir

{
 "type": "action",
 "action": "list_dir",
 "value": "."
}

Ejemplo completo:

{
 "name": "organize_pdfs",
 "trigger": "manual",
 "steps": [
  {
   "type": "action",
   "action": "create_folder",
   "value": "PDF"
  },
  {
   "type": "action",
   "action": "move_files",
   "value": {
    "ext": ".pdf",
    "to": "PDF"
   }
  }
 ]
}

No expliques nada.
Devuelve SOLO JSON válido.
"""


# ==========================================================
# PARSE SCHEDULE FROM NATURAL LANGUAGE
# ==========================================================

def parse_schedule(prompt):

    prompt = prompt.lower()

    # cada X minutos
    m = re.search(r"cada (\d+) minutos?", prompt)
    if m:
        return int(m.group(1)) * 60

    # cada X horas
    m = re.search(r"cada (\d+) horas?", prompt)
    if m:
        return int(m.group(1)) * 3600

    # cada hora
    if "cada hora" in prompt:
        return 3600

    # cada día
    if "cada día" in prompt or "cada dia" in prompt:
        return 86400

    return None


# ==========================================================
# COPILOT ENGINE
# ==========================================================

class CopilotEngine:

    def interpret(self, prompt):

        interval = parse_schedule(prompt)

        full_prompt = SYSTEM_PROMPT + "\n\n" + prompt

        r = requests.post(
            OLLAMA_URL,
            json={
                "model": "llama3",
                "prompt": full_prompt,
                "stream": False
            }
        )

        data = r.json()

        content = data.get("response", "")

        try:

            workflow = json.loads(content)

            # si detectamos intervalo temporal
            if interval:
                workflow["trigger"] = "schedule"
                workflow["interval"] = interval

            return workflow

        except Exception:
            return None


# instancia global
copilot = CopilotEngine()