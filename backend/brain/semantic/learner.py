from brain.semantic.store import save_semantic


def learn_from_interaction(user_id, message, response):

    lower = message.lower()

    # ejemplo simple
    if "siempre abrí" in lower:
        app = lower.replace("siempre abrí", "").strip()
        save_semantic(user_id, "default_app", app)

    if "prefiero" in lower:
        pref = lower.replace("prefiero", "").strip()
        save_semantic(user_id, "preference", pref)