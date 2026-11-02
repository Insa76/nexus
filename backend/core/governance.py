def evaluate_mode_request(requested_mode, metrics, circuit_state):

    if requested_mode == "aggressive":

        if any(state == "OPEN" for state in circuit_state.values()):
            return "stable", "Riesgo sistémico detectado"

        if metrics.get("error_rate", 0) > 0.2:
            return "efficient", "Tasa de error elevada"

    return requested_mode, None