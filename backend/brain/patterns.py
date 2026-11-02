from collections import Counter
from core.database import get_connection


def analyze_patterns(limit=200):

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
    SELECT step_name FROM step_executions
    ORDER BY started_at DESC
    LIMIT %s
    """, (limit,))

    rows = cur.fetchall()
    conn.close()

    steps = [r["step_name"] for r in rows]

    counter = Counter(steps)

    suggestions = []

    for step, count in counter.items():

        if count >= 5:
            suggestions.append({
                "type": "repeated_step",
                "step": step,
                "count": count,
                "message": f"Detecté que ejecutás '{step}' {count} veces. ¿Querés automatizarlo?"
            })

    return suggestions