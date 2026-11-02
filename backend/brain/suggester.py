from brain.llm import ask_llm

SYSTEM_PROMPT = """
Sos un experto en automatización.

Generá un workflow JSON válido basado en este patrón repetitivo.

Formato:

{
 "name": "...",
 "trigger": {"type":"manual"},
 "steps": [...]
}
"""

def generate_suggestion(pattern):

    prompt = f"""
{SYSTEM_PROMPT}

Patrón detectado:
{pattern}
"""

    return ask_llm(prompt)