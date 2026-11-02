import uuid

from core.database import get_connection

from core.workflow_generator import (
    generate_workflow
)

from jobs.manager import manager


async def create_mission(

    goal,
    model="llama3"
):

    mission_id = str(uuid.uuid4())

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO missions
        (
            id,
            goal,
            status
        )
        VALUES (%s,%s,%s)
    """, (
        mission_id,
        goal,
        "planning"
    ))

    conn.commit()

    # =========================
    # GENERATE DAG
    # =========================
    workflow = generate_workflow(
        goal,
        model
    )

    # =========================
    # EXECUTE
    # =========================
    job_id = await manager.create_job(
        workflow,
        "system"
    )

    # =========================
    # UPDATE
    # =========================
    cur.execute("""
        UPDATE missions
        SET status = %s,
            result = %s
        WHERE id = %s
    """, (
        "running",
        str({
            "job_id": job_id
        }),
        mission_id
    ))

    conn.commit()
    conn.close()

    return {
        "mission_id": mission_id,
        "job_id": job_id
    }