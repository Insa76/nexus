def explain_decision(decision, snapshot):

    action = decision.get("action")

    if action == "reduce_workers":

        return (
            f"He reducido los workers porque la tasa de error "
            f"alcanzó {round(snapshot['error_rate']*100,2)}%."
        )

    if action == "scale_workers":

        return (
            f"He aumentado los workers porque la cola de trabajos "
            f"llegó a {snapshot['queue_size']}."
        )

    if action == "force_stable_mode":

        return (
            "Activé modo estable porque hay circuit breakers abiertos."
        )

    if action == "investigate":

        return decision.get("reason")

    return "He tomado una acción automática para proteger el sistema."