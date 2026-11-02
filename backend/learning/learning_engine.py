from core.database import get_connection
from datetime import datetime


class LearningEngine:

    def analyze_recent_failures(self):

        conn = get_connection()
        cur = conn.cursor()

        cur.execute("""
            SELECT workflow, result
            FROM jobs
            WHERE status='error'
            ORDER BY updated_at DESC
            LIMIT 20
        """)

        rows = cur.fetchall()
        conn.close()

        if not rows:
            return None

        workflows = {}

        for r in rows:

            wf = r["workflow"]

            workflows[wf] = workflows.get(wf, 0) + 1

        for wf, count in workflows.items():

            if count >= 3:

                return {
                    "type": "repeated_failure",
                    "workflow": wf,
                    "message": f"El workflow {wf} está fallando repetidamente."
                }

        return None


    def save_learning(self, learning):

        conn = get_connection()
        cur = conn.cursor()

        cur.execute("""
            INSERT INTO nexus_learning
            (timestamp, type, workflow, message)
            VALUES (%s, %s, %s, %s)
        """, (
            datetime.utcnow(),
            learning["type"],
            learning.get("workflow"),
            learning["message"]
        ))

        conn.commit()
        conn.close()


learning_engine = LearningEngine()