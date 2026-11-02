import json
from ai.ollama_client import ask_ollama


SYSTEM_PROMPT = """
You are an automation engine.

Return ONLY valid JSON.

Schema:

{
 "name": "workflow_name",
 "trigger": "manual",
 "steps":[
   {
     "type":"action",
     "action":"create_folder",
     "value":"folder"
   }
 ]
}

Allowed actions:

create_folder
move_files
list_dir
read_file
write_file
delete_file
run_cmd
open_url
"""


def generate_workflow(prompt):

    full_prompt = SYSTEM_PROMPT + "\n\nUser request:\n" + prompt

    response = ask_ollama(full_prompt)

    try:
        workflow = json.loads(response)
    except:
        raise Exception("LLM devolvió JSON inválido")

    return workflow