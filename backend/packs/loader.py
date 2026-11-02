import json
from pathlib import Path
import sqlite3

DB = "nexus.db"
PACKS_DIR = Path("packs")


def list_packs():

    packs = []

    if not PACKS_DIR.exists():
        return packs

    for p in PACKS_DIR.iterdir():

        cfg = p / "pack.json"

        if cfg.exists():
            try:
                data = json.loads(cfg.read_text())
                packs.append(data)
            except:
                continue

    return packs


def install_pack(slug):

    pack_dir = PACKS_DIR / slug

    if not pack_dir.exists():
        return False

    workflows_file = pack_dir / "workflows.json"

    if not workflows_file.exists():
        return False

    tpl = json.loads(workflows_file.read_text())

    conn = sqlite3.connect(DB)
    cur = conn.cursor()

    for wf in tpl:

        # insertar workflow
        cur.execute("""
            INSERT INTO workflows (name, version, tenant_id)
            VALUES (?, ?, ?)
        """, (
            wf["name"],
            1,
            "default"
        ))

        workflow_id = cur.lastrowid

        # insertar steps
        for i, step in enumerate(wf.get("steps", [])):

            cur.execute("""
                INSERT INTO workflow_steps
                (workflow_id, step_order, action, value, config)
                VALUES (?, ?, ?, ?, ?)
            """, (
                workflow_id,
                i,
                step["action"],
                json.dumps(step.get("value")),
                json.dumps(step.get("config", {}))
            ))

    conn.commit()
    conn.close()

    return True