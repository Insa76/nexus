from brain.multi.planner import plan_task
from brain.multi.executor import execute_plan
from brain.multi.critic import evaluate


def run_multi_agent(message, user=None):

    print("🧠 Planner creando plan...")
    plan = plan_task(message)

    print("⚙️ Executor ejecutando...")
    result = execute_plan(plan)

    joined = "\n".join(result)

    print("🔍 Critic evaluando...")
    ok = evaluate(joined)

    if ok:
        return joined

    print("🔁 Reintentando una vez...")
    result = execute_plan(plan, user)

    return "\n".join(result)
