from workflows.repository import get_workflow_by_name, save_workflow_version


def improve_workflow(workflow_name, tenant_id="default", workspace_id="main"):

    wf = get_workflow_by_name(workflow_name, tenant_id, workspace_id)

    if not wf:
        return None

    steps = wf.get("steps", [])

    improved = False
    new_steps = []

    for step in steps:

        action = step.get("action")

        if action == "move_files":

            value = step.get("value", {})

            if isinstance(value, dict):

                folder = value.get("to")

                # agregar create_folder antes
                new_steps.append({
                    "type":"action",
                    "action":"create_folder",
                    "value":folder
                })

                improved = True

        new_steps.append(step)

    if not improved:
        return None

    new_version = save_workflow_version(
        wf["name"],
        wf.get("trigger","manual"),
        new_steps,
        tenant_id,
        workspace_id
    )

    return {
        "workflow": workflow_name,
        "new_version": new_version
    }