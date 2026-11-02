from core.database import get_connection
from datetime import datetime, timedelta


FAIL_THRESHOLD = 5
COOLDOWN_MINUTES = 10


def check_workflow_health(workflow_name):

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT COUNT(*) as fails
        FROM jobs
        WHERE workflow=%s
        AND status='error'
        AND updated_at > datetime('now','-10 minutes')
    """,(workflow_name,))

    row = cur.fetchone()

    conn.close()

    if row["fails"] >= FAIL_THRESHOLD:
        return False

    return True


def disable_workflow(workflow_name):

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        UPDATE workflows
        SET active=0
        WHERE name=%s
    """,(workflow_name,))

    conn.commit()
    conn.close()


def enable_workflow(workflow_name):

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        UPDATE workflows
        SET active=1
        WHERE name=%s
    """,(workflow_name,))

    conn.commit()
    conn.close()