import json
from brain.llm import ask_llm  # usa tu wrapper actual del LLM


SYSTEM_PROMPT = """
Sos un planificador de automatizaciones.

Convertí la instrucción del usuario en un workflow JSON.

Reglas:
- devolver SOLO JSON válido
- formato:

{
 "name": "nombre",
 "trigger": "manual",
 "steps": [
   {"action":"list_dir","value":"."}
 ]
}

Acciones disponibles:
open_app
open_url
list_dir
read_file
write_file
delete_file
copy_file
rename_file
create_folder
move_files
list_processes
kill_process
get_time
run_cmd
sleep

NO inventes acciones nuevas.
"""


def generate_workflow(text: str):

    prompt = f"{SYSTEM_PROMPT}\n\nUsuario: {text}"

    raw = ask_llm(prompt)

    try:
        data = json.loads(raw)
        return data
    except:
        return {
            "error": "No se pudo generar workflow",
            "raw": raw
        }