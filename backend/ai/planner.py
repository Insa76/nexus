import json
from ai.ollama_client import ask_ollama
from memory.nexus_memory import load_memory


PLANNER_PROMPT = """
You are an AI system planner.

Your task is to create a plan to automate a user request.

Return JSON only.

Schema:

{
 "goal": "user goal",
 "plan": [
   "step 1",
   "step 2"
 ]
}
"""


def create_plan(user_prompt):

    memory = load_memory()

    memory_context = json.dumps(memory)

    full_prompt = (
        PLANNER_PROMPT
        + "\n\nSystem memory:\n"
        + memory_context
        + "\n\nUser request:\n"
        + user_prompt
    )

    response = ask_ollama(full_prompt)

    try:
        plan = json.loads(response)
    except:
        raise Exception("Planner devolvió JSON inválido")

    return plan


def plan_to_workflow(plan):

    steps = []

    for p in plan["plan"]:

        text = p.lower()

        if "carpeta" in text:

            steps.append({
                "type": "action",
                "action": "create_folder",
                "value": "data"
            })

        elif "mover" in text:

            steps.append({
                "type": "action",
                "action": "move_files",
                "value": {
                    "ext": ".pdf",
                    "to": "PDF"
                }
            })

        elif "listar" in text:

            steps.append({
                "type": "action",
                "action": "list_dir",
                "value": "."
            })

    return {
        "name": "ai_generated_workflow",
        "trigger": "manual",
        "steps": steps
    }