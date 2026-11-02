class AnomalyDetector:

    def detect(self, history):

        if len(history) < 5:
            return None

        last = history[-1]
        prev = history[-5]

        # error spike
        if last["error_rate"] > prev["error_rate"] * 2 and last["error_rate"] > 0.2:
            return {
                "type": "error_spike",
                "message": "Estoy observando un aumento anormal de errores."
            }

        # queue growth
        if last["queue_size"] > prev["queue_size"] + 10:
            return {
                "type": "queue_growth",
                "message": "La cola de trabajos está creciendo rápidamente."
            }

        if len(last["open_circuits"]) >= 2:
            return {
                "type": "circuit_alert",
                "message": "Varios circuit breakers están abiertos."
            }

        return None


anomaly_detector = AnomalyDetector()