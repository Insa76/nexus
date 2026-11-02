import json
from datetime import datetime, timezone

from core.database import get_connection


# ==========================================================
# SAVE WORKFLOW VERSION
# ==========================================================

def save_workflow_version(
    name,
    trigger,
    steps,
    tenant_id="default",
    workspace_id="main"
):

    conn = get_connection()
    cur = conn.cursor()

    # 1️⃣ Obtener versión actual
    cur.execute("""
        SELECT MAX(version)
        FROM workflows
        WHERE name = %s
        AND tenant_id = %s
        AND workspace_id = %s
    """, (name, tenant_id, workspace_id))

    row = cur.fetchone()
    current_version = row[0] if row and row[0] else 0
    new_version = current_version + 1

    # 2️⃣ Desactivar versiones anteriores
    cur.execute("""
        UPDATE workflows
        SET active = FALSE
        WHERE name = %s
        AND tenant_id = %s
        AND workspace_id = %s
    """, (name, tenant_id, workspace_id))

    # 3️⃣ Crear definición
    definition = {
        "name": name,
        "trigger": trigger,
        "steps": steps
    }

    now = datetime.now(timezone.utc)

    # 4️⃣ Insertar nueva versión activa
    cur.execute("""
        INSERT INTO workflows
        (name, version, definition, created_at, tenant_id, workspace_id, active)
        VALUES (%s, %s, %s, %s, %s, %s, TRUE)
    """, (
        name,
        new_version,
        json.dumps(definition),
        now,
        tenant_id,
        workspace_id
    ))

    conn.commit()
    conn.close()

    return new_version


# ==========================================================
# GET WORKFLOW ACTIVO
# ==========================================================

def get_workflow_by_name(name, tenant_id="default", workspace_id="main"):

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT definition
        FROM workflows
        WHERE name = %s
        AND tenant_id = %s
        AND workspace_id = %s
        AND active = 1
        ORDER BY version DESC
        LIMIT 1
    """, (name, tenant_id, workspace_id))

    row = cur.fetchone()
    conn.close()

    if not row:
        return None

    definition = row[0]

    if not definition:
        raise Exception("Workflow definition vacía en DB")

    return json.loads(definition)


# ==========================================================
# LIST WORKFLOWS
# ==========================================================

def load_workflows(tenant_id="default", workspace_id="main"):

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT name, version
        FROM workflows
        WHERE tenant_id = %s
        AND workspace_id = %s
        AND active = 1
    """, (tenant_id, workspace_id))

    rows = cur.fetchall()
    conn.close()

    return [
        {
            "name": r[0],
            "version": r[1]
        }
        for r in rows
    ]


# ==========================================================
# GET WORKFLOWS BY TRIGGER
# ==========================================================

def get_workflows_by_trigger(trigger, tenant_id="default", workspace_id="main"):

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT definition
        FROM workflows
        WHERE tenant_id = %s
        AND workspace_id = %s
        AND active = 1
    """, (tenant_id, workspace_id))

    rows = cur.fetchall()
    conn.close()

    matched = []

    for row in rows:
        wf = json.loads(row[0])
        if wf.get("trigger") == trigger:
            matched.append(wf)

    return matched