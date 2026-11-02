from core.database import get_connection


class CopilotDebugger:

    def analyze_last_failure(self):

        conn = get_connection()
        cur = conn.cursor()

        # último job fallido
        cur.execute("""
            SELECT id, workflow, result, updated_at
            FROM jobs
            WHERE status='error'
            ORDER BY updated_at DESC
            LIMIT 1
        """)

        job = cur.fetchone()

        if not job:
            conn.close()
            return {
                "message": "No encontré workflows fallidos recientemente."
            }

        job_id = job["id"]

        # pasos del job
        cur.execute("""
            SELECT step, status, result
            FROM job_steps
            WHERE job_id=%s
        """,(job_id,))

        steps = cur.fetchall()

        conn.close()

        failed_step = None

        for s in steps:
            if s["status"] == "error":
                failed_step = s
                break

        if failed_step:

            return {
                "workflow": job["workflow"],
                "message": f"El workflow falló en el paso '{failed_step['step']}'.",
                "error": failed_step["result"]
            }

        return {
            "workflow": job["workflow"],
            "message": "El workflow falló pero no encontré el paso exacto."
        }


debugger = CopilotDebugger()