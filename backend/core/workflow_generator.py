import json
import re

from core.ai_agent import ask_agent


def generate_workflow(

    goal,
    model="llama3"
):

    prompt = f"""
You are an AI workflow architect.

Goal:
{goal}

Available actions:

- create_folder
- move_files
- open_url
- if_extension
- approval
- join

Generate a workflow graph.

Respond ONLY valid JSON.

Format:

{{
  "nodes": [],
  "edges": []
}}
"""

    response = ask_agent(
        prompt,
        model
    )

    print(f"🧠 DAG RAW: {response}")

    match = re.search(
        r"\{.*\}",
        response,
        re.DOTALL
    )

    if not match:

        return None

    return json.loads(
        match.group(0)
    )