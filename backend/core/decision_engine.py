class DecisionEngine:

    def decide(self, snapshot, risk, anomaly):

        # riesgo alto
        if risk == "HIGH":
            return {
                "action": "force_stable_mode",
                "reason": "Riesgo alto detectado"
            }

        # anomalía detectada
        if anomaly:
            return {
                "action": "investigate",
                "reason": anomaly["message"]
            }

        # cola creciendo
        if snapshot["queue_size"] > 20:
            return {
                "action": "scale_workers",
                "reason": "Cola de trabajos elevada"
            }

        return None


decision_engine = DecisionEngine()