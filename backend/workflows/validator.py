VALID_ACTIONS = {
    "create_folder",
    "move_files",
    "list_dir",
    "read_file",
    "write_file",
    "delete_file",
    "run_cmd",
    "open_url"
}

# acciones que requieren confirmación humana
DANGEROUS_ACTIONS = {
    "delete_file",
    "run_cmd"
}

MAX_STEPS = 25


def validate_workflow(workflow):

    if not workflow:
        raise Exception("Workflow vacío")

    if "steps" not in workflow:
        raise Exception("Workflow sin steps")

    steps = workflow["steps"]

    if not isinstance(steps, list):
        raise Exception("Steps debe ser una lista")

    if len(steps) > MAX_STEPS:
        raise Exception("Workflow demasiado grande")

    for step in steps:
        validate_step(step)

    return workflow


def validate_step(step):

    if not isinstance(step, dict):
        raise Exception("Step inválido")

    if "action" not in step and step.get("type") != "condition":
        raise Exception("Step sin acción")

    # =========================
    # ACTION STEPS
    # =========================

    if "action" in step:

        action = step["action"]

        if action not in VALID_ACTIONS:
            raise Exception(f"Acción no válida: {action}")

        # advertencia acciones peligrosas
        if action in DANGEROUS_ACTIONS:
            print(f"⚠ Acción peligrosa detectada: {action}")

        value = step.get("value")

        # ---------------------
        # autocorrecciones
        # ---------------------

        if action == "move_files":

            if isinstance(value, str):

                step["value"] = {
                    "ext": ".pdf",
                    "to": "PDF"
                }

        if action == "list_dir":

            if not value:
                step["value"] = "."

    # =========================
    # SUBSTEPS (next)
    # =========================

    if "next" in step:

        if not isinstance(step["next"], list):
            raise Exception("next debe ser lista")

        for s in step["next"]:
            validate_step(s)

    # =========================
    # CONDITIONS
    # =========================

    if step.get("type") == "condition":

        for branch in ["then", "else_"]:

            if branch in step:

                if not isinstance(step[branch], list):
                    raise Exception(f"{branch} debe ser lista")

                for s in step[branch]:
                    validate_step(s)