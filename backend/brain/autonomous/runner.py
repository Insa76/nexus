from brain.autonomous.agent import next_step
from actions.system_actions import execute_action
import time


MAX_STEPS = 10


def run_autonomous(goal, user=None):

    history = []
    step_count = 0

    while step_count < MAX_STEPS:

        plan = next_step(goal, history)

        if plan.get("done"):
            break

        steps = plan.get("steps", [])

        for s in steps:
            out = execute_action(s["action"], s["value"], user)
            history.append(out)

        step_count += 1
        time.sleep(1)

    return "\n".join(history)
