from core.metrics import metrics
from resilience.circuit import circuit
from core.database import get_connection
from datetime import datetime
import json


class SelfModel:

    def __init__(self):
        self.last_evaluation = None
        self.history = []

    # =========================
    # SYSTEM SNAPSHOT
    # =========================

    def snapshot(self):

        errors = metrics.counters.get("jobs_failed", 0)
        done = metrics.counters.get("jobs_done", 0)

        total = errors + done

        error_rate = errors / total if total > 0 else 0

        open_circuits = [
            k for k, v in circuit.state.items()
            if v == "OPEN"
        ]

        queue_size = metrics.gauges.get("active_jobs", 0)

        snapshot = {
            "timestamp": datetime.utcnow().isoformat(),
            "error_rate": error_rate,
            "open_circuits": open_circuits,
            "queue_size": queue_size,
            "total_jobs": total
        }

        # guardar historial
        self.history.append(snapshot)

        # mantener historial corto (~5 minutos si loop es 10s)
        if len(self.history) > 30:
            self.history.pop(0)

        return snapshot

    # =========================
    # RISK EVALUATION
    # =========================

    def evaluate_risk(self, snapshot):

        if snapshot["open_circuits"]:
            return "HIGH"

        if snapshot["error_rate"] > 0.3:
            return "MEDIUM"

        return "LOW"

    # =========================
    # HEALTH SCORE
    # =========================

    def health_score(self, snapshot):

        score = 100

        # penalizar error rate
        score -= snapshot["error_rate"] * 50

        # penalizar circuit breakers abiertos
        score -= len(snapshot["open_circuits"]) * 20

        # penalizar cola grande
        if snapshot["queue_size"] > 10:
            score -= 10

        if score < 0:
            score = 0

        return round(score, 2)

    # =========================
    # ANOMALY DETECTION
    # =========================

    def detect_anomaly(self):

        if len(self.history) < 5:
            return None

        last = self.history[-1]
        prev = self.history[-5]

        # spike de errores
        if last["error_rate"] > prev["error_rate"] * 2 and last["error_rate"] > 0.2:
            return {
                "type": "error_spike",
                "message": "He detectado un aumento abrupto en la tasa de errores."
            }

        # crecimiento de cola
        if last["queue_size"] > prev["queue_size"] + 10:
            return {
                "type": "queue_growth",
                "message": "La cola de trabajos está creciendo rápidamente."
            }

        # múltiples circuitos abiertos
        if len(last["open_circuits"]) >= 2:
            return {
                "type": "multiple_circuits",
                "message": "Varios circuit breakers están abiertos."
            }

        return None

    # =========================
    # DECISION ENGINE
    # =========================

    def propose_action(self, snapshot, risk):

        if risk == "HIGH":
            return {
                "action": "force_stable_mode",
                "reason": "Circuitos abiertos detectados"
            }

        if risk == "MEDIUM":
            return {
                "action": "reduce_workers",
                "reason": "Tasa de error elevada"
            }

        return None

    # =========================
    # DECISION LOG
    # =========================

    def log_decision(self, decision):

        conn = get_connection()
        cur = conn.cursor()

        cur.execute("""
            INSERT INTO decisions_log
            (timestamp, action, reason)
            VALUES (%s, %s, %s)
        """, (
            datetime.utcnow(),
            decision["action"],
            decision["reason"]
        ))

        conn.commit()
        conn.close()


self_model = SelfModel()