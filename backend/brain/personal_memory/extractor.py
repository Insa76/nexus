IMPORTANT = [
    "proyecto",
    "cliente",
    "decidimos",
    "acordamos",
    "usar",
    "configurar",
    "preferencia"
]


def should_remember(text):

    t = text.lower()

    return any(word in t for word in IMPORTANT)
