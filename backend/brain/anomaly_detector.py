class AnomalyDetector:

    def __init__(self):
        self.history = []

    def detect(self, history):

        # Si no hay suficiente historial no detectamos anomalías
        if len(history) < 5:
            return False

        # ejemplo simple: muchos errores seguidos
        errors = [h for h in history[-5:] if h.get("status") == "error"]

        if len(errors) >= 3:
            return True

        return False


anomaly_detector = AnomalyDetector()