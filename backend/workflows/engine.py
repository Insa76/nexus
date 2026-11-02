import asyncio
import uuid
from datetime import datetime
import json

from core.database import get_connection
from actions.system_actions import execute_action
from realtime.ws import manager
from events.bus import bus
from workflows.repository import get_workflow_by_name
from workflows.types import validate_type


# ==========================================================
# RUN WORKFLOW (ENTRYPOINT OFICIAL)
# ==========================================================

async def run_workflow(
    name,
    tenant_id=None,
    workspace_id=None,
    job_id=None,
    user=None,
    shared_context=None
):

    wf = get_workflow_by_name(
        name,
        tenant_id=tenant_id,
        workspace_id=workspace_id
    )

    if not wf:
        raise Exception("Workflow no encontrado")

    context = shared_context if shared_context is not None else {}
    history = []

    for step in wf["steps"]:
        result = await execute_step(
            step,
            user,
            context,
            workflow_name=name,
            tenant_id=tenant_id,
            workspace_id=workspace_id,
            job_id=job_id
        )
        history.extend(result)

    return history


# ==========================================================
# EXECUTE STEP (MOTOR REAL)
# ==========================================================

async def execute_step(
    step,
    user,
    context,
    workflow_name=None,
    tenant_id=None,
    workspace_id=None,
    job_id=None
):

    history = []
    step_type = step.get("type", "action")

    try:

        # ==================================================
        # 1️⃣ ACCIÓN NORMAL
        # ==================================================

        if step_type == "action":

            value = resolve_variables(step.get("value"), context)

            if step.get("input_type"):
                if not validate_type(value, step.get("input_type")):
                    raise Exception(
                        f"Input inválido para {step['action']}"
                    )

            await bus.publish("step.start", {
                "workflow": workflow_name,
                "step": step["action"],
                "job_id": job_id
            })

            out = execute_action(
                step["action"],
                value,
                user
            )

            # 🔥 FIX IMPORTANTE (si la acción es async)
            if asyncio.iscoroutine(out):
                out = await out

            if step.get("output_type"):
                if not validate_type(out, step.get("output_type")):
                    raise Exception(
                        f"Output inválido en {step['action']}"
                    )

            if step.get("assign"):
                context[step["assign"]] = out

            history.append({
                "type": "action",
                "action": step["action"],
                "result": out
            })

            # 🔥 LOG DEL STEP
            log_step(job_id, step["action"], "success", out)

            await bus.publish("step.success", {
                "workflow": workflow_name,
                "step": step["action"],
                "job_id": job_id
            })

            await manager.broadcast({
                "type": "workflow_step",
                "action": step["action"]
            })

            await manager.broadcast({
                "type": "workflow_result",
                "action": step["action"],
                "result": out
            })

            for child in step.get("next", []):
                child_result = await execute_step(
                    child,
                    user,
                    context,
                    workflow_name,
                    tenant_id,
                    workspace_id,
                    job_id
                )
                history.extend(child_result)

            return history


        # ==================================================
        # 2️⃣ CONDICIÓN
        # ==================================================

        if step_type == "condition":

            test_value = resolve_variables(
                step.get("value"),
                context
            )

            test_result = execute_action(
                step["if_action"],
                test_value,
                user
            )

            if asyncio.iscoroutine(test_result):
                test_result = await test_result

            condition_met = evaluate_condition(
                test_result,
                step.get("operator"),
                step.get("compare")
            )

            history.append({
                "type": "condition",
                "result": condition_met
            })

            branch = step.get("then") if condition_met else step.get("else_")

            if branch:
                for s in branch:
                    branch_result = await execute_step(
                        s,
                        user,
                        context,
                        workflow_name,
                        tenant_id,
                        workspace_id,
                        job_id
                    )
                    history.extend(branch_result)

            return history


        # ==================================================
        # 3️⃣ SUBWORKFLOW
        # ==================================================

        if step_type == "subworkflow":

            sub_name = step.get("name")

            await manager.broadcast({
                "type": "workflow_sub_start",
                "workflow": sub_name
            })

            sub_history = await run_workflow(
                sub_name,
                tenant_id=tenant_id,
                workspace_id=workspace_id,
                job_id=job_id,
                user=user,
                shared_context=context
            )

            history.append({
                "type": "subworkflow",
                "workflow": sub_name,
                "result": sub_history
            })

            await manager.broadcast({
                "type": "workflow_sub_end",
                "workflow": sub_name
            })

            return history

        return history


    except Exception as e:

        error = str(e)

        print("🔥 ERROR REAL:", repr(e))

        await bus.publish("step.error", {
            "workflow": workflow_name,
            "step": step.get("action"),
            "error": error,
            "job_id": job_id,
            "tenant_id": tenant_id,
            "workspace_id": workspace_id
        })

        await manager.broadcast({
            "type": "workflow_error",
            "error": error
        })

        history.append({
            "type": "error",
            "step": step.get("action"),
            "error": error
        })

        log_step(job_id, step.get("action"), "error", str(e))

        raise


# ==========================================================
# VARIABLE RESOLUTION
# ==========================================================

def resolve_variables(value, context):

    if value is None:
        return value

    if isinstance(value, str):
        for key, val in context.items():
            placeholder = "{{" + key + "}}"
            if placeholder in value:
                value = value.replace(
                    placeholder,
                    str(val)
                )
        return value

    if isinstance(value, dict):
        return {
            k: resolve_variables(v, context)
            for k, v in value.items()
        }

    return value


# ==========================================================
# CONDITION EVALUATOR
# ==========================================================

def evaluate_condition(result, operator, compare):

    if operator == "contains":
        return str(compare) in str(result)

    if operator == "equals":
        return str(result) == str(compare)

    if operator == "not_equals":
        return str(result) != str(compare)

    if operator == "gt":
        try:
            return float(result) > float(compare)
        except:
            return False

    if operator == "lt":
        try:
            return float(result) < float(compare)
        except:
            return False

    return False


# ==========================================================
# STEP LOG
# ==========================================================

def log_step(job_id, step, status, result):

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO job_steps
        (job_id, step, status, result, timestamp)
        VALUES (%s, %s, %s, %s, %s)
    """, (
        job_id,
        step,
        status,
        json.dumps(result) if result else "",
        datetime.utcnow()
    ))

    conn.commit()
    conn.close()