from actions.system_actions import execute_action


def execute_plan(plan, user=None):

    outputs = []

    for step in plan.get("steps", []):
        out = execute_action(step["action"], step["value"], user)
        outputs.append(out)

    return outputs
