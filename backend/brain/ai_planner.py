import requests

OLLAMA_URL = "http://localhost:11434/api/generate"

MODEL = "llama3"


def generate_workflow(task):

    prompt = f"""
You are an automation system.

Convert the user request into a workflow JSON.

Available actions:
- list_dir
- move_files
- create_folder
- read_file
- write_file

User request:
{task}

Return only valid JSON.
"""

    r = requests.post(
        OLLAMA_URL,
        json={
            "model": MODEL,
            "prompt": prompt,
            "stream": False
        }
    )

    data = r.json()

    return data["response"]