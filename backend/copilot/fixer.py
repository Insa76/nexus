from core.database import get_connection


class CopilotFixer:

    def propose_fix(self):

        conn = get_connection()
        cur = conn.cursor()

        # último job fallido
        cur.execute("""
            SELECT id, workflow, result
            FROM jobs
            WHERE status='error'
            ORDER BY updated_at DESC
            LIMIT 1
        """)

        job = cur.fetchone()

        if not job:
            conn.close()
            return {
                "message": "No encontré errores recientes."
            }

        error_text = job["result"] or ""

        suggestion = None

        # =========================
        # REGLAS DE CORRECCIÓN
        # =========================

        if "File not found" in error_text:
            suggestion = {
                "action": "add_step",
                "step": {
                    "type": "action",
                    "action": "create_folder",
                    "value": "missing_folder"
                },
                "reason": "El workflow intenta leer un archivo que no existe."
            }

        elif "Ruta no permitida" in error_text:
            suggestion = {
                "action": "change_path",
                "reason": "La ruta está bloqueada por sandbox."
            }

        elif "Workflow no encontrado" in error_text:
            suggestion = {
                "action": "verify_workflow_name",
                "reason": "El workflow solicitado no existe en la base de datos."
            }

        else:
            suggestion = {
                "action": "manual_review",
                "reason": "No pude determinar automáticamente la causa."
            }

        conn.close()

        return {
            "workflow": job["workflow"],
            "error": error_text,
            "suggestion": suggestion
        }


fixer = CopilotFixer()