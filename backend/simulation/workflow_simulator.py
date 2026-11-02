from workflows.repository import get_workflow_by_name


def simulate_workflow(name, tenant_id="default", workspace_id="main"):

    wf = get_workflow_by_name(name, tenant_id, workspace_id)

    if not wf:
        return {"error":"workflow no encontrado"}

    risks=[]
    steps = wf.get("steps", [])

    for step in steps:

        action = step.get("action")

        # riesgo común
        if action == "move_files":

            value = step.get("value",{})

            if isinstance(value,dict):

                folder = value.get("to")

                if not folder:
                    risks.append({
                        "step":"move_files",
                        "risk":"destino no definido"
                    })

        if action == "delete_file":

            risks.append({
                "step":"delete_file",
                "risk":"acción destructiva"
            })

    return {
        "workflow": name,
        "steps": len(steps),
        "risks": risks,
        "safe": len(risks) == 0
    }