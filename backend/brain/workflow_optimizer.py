from core.database import get_connection


def analyze_workflows():

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT step, status, COUNT(*) as total
        FROM job_steps
        GROUP BY step, status
    """)

    rows = cur.fetchall()
    conn.close()

    problems = []

    for r in rows:

        step = r["step"]
        status = r["status"]
        total = r["total"]

        if status == "error" and total > 2:

            problems.append({
                "step": step,
                "issue": "step falla frecuentemente",
                "count": total
            })

    return problems

from core.database import get_connection


def analyze_workflows():

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT step, status, COUNT(*) as total
        FROM job_steps
        GROUP BY step, status
    """)

    rows = cur.fetchall()
    conn.close()

    problems = []

    for r in rows:

        step = r["step"]
        status = r["status"]
        total = r["total"]

        if status == "error" and total > 2:

            problems.append({
                "step": step,
                "issue": "step falla frecuentemente",
                "count": total
            })

    return problems

def suggest_fixes(problems):

    suggestions = []

    for p in problems:

        step = p["step"]

        if step == "move_files":

            suggestions.append({
                "step": step,
                "suggestion": "verificar que la carpeta destino exista"
            })

        if step == "read_file":

            suggestions.append({
                "step": step,
                "suggestion": "validar que el archivo exista antes"
            })

    return suggestions    