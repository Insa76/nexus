from learning.habits import detect_habits


def get_suggestions():

    habits = detect_habits()

    if not habits:
        return []

    suggestions = []

    for action, times in habits:
        suggestions.append(
            f"Hacés '{action}' muy seguido ({times} veces). ¿Querés automatizarlo?"
        )

    return suggestions
