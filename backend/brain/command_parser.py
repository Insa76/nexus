def parse_local_command(text: str):
    t = text.lower().strip()

    # hora
    if "hora" in t:
        return {"action": "get_time"}

    # abrir app
    if t.startswith("abrir ") or t.startswith("abrí ") or t.startswith("open "):
        app = t.split(" ", 1)[1]
        return {"action": "open_app", "value": app}

    return None
