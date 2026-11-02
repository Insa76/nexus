import requests
import re

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "llama3"


SYSTEM_PROMPT = """
Sos un generador de workflows para automatización de archivos en PC.
RESPONDÉ SOLO JSON VÁLIDO.
NO agregues texto antes ni después.
NO expliques nada.

IMPORTANTE:
- NO busques en internet
- NO uses open_url salvo que el usuario lo pida explícitamente
- SIEMPRE priorizar acciones de sistema

Formato obligatorio JSON:

{
  "steps": [
    {
      "action": "string",
      "value": {}
    }
  ]
}

Acciones permitidas:
- create_folder { "path": string }
- move_files { "ext": string, "to": string }
- open_url { "url": string }

Ejemplo correcto:

Usuario: ordenar pdf

Respuesta:
{
  "steps": [
    {
      "action": "create_folder",
      "value": {"path": "PDF"}
    },
    {
      "action": "move_files",
      "value": {"ext": ".pdf", "to": "PDF"}
    }
  ]
}
"""


def extract_json(text):

    match = re.search(r"\{.*\}", text, re.DOTALL)

    if match:
        return match.group(0)

    return None


def generate_steps(prompt: str):

    full_prompt = f"{SYSTEM_PROMPT}\n\nUsuario: {prompt}"

    try:

        response = requests.post(
            OLLAMA_URL,
            json={
                "model": MODEL,
                "prompt": full_prompt,
                "stream": False
            },
            timeout=60
        )

        print("🔌 STATUS:", response.status_code)
        print("🔌 RAW RESPONSE:", response.text)

        response.raise_for_status()

        data = response.json()

        text = data.get("response", "").strip()

        print("🧠 RAW LLM:", text)

        return text

    except Exception as e:

        print("❌ LLM CONNECTION ERROR:", str(e))

        raise Exception(f"Ollama error: {str(e)}")