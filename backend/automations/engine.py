import asyncio
from actions.system_actions import execute_action


# ==========================================================
# VERSION ASYNC REAL
# ==========================================================

async def run_steps_async(steps):

    outputs = []

    for step in steps:
        result = await execute_action(
            step["action"],
            step.get("value")
        )
        outputs.append(str(result))

    return "\n".join(outputs)


# ==========================================================
# Wrapper sync (para scheduler viejo)
# ==========================================================

def run_steps(steps):
    return asyncio.run(run_steps_async(steps))