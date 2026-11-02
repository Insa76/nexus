import pytest

from planner.intent_recognizer import IntentRecognizer


@pytest.mark.parametrize(
    "phrase",
    [
        "¿Qué hora es?",
        "Que hora es",
        "Decime la hora",
        "Decíme la hora",
        "Dime la hora",
        "Decime qué hora es",
        "¿Qué hora tenemos?",
        "¿Me decís la hora?",
        "Decime la fecha y hora actual del sistema.",
    ],
)
def test_recognizes_time_intent(phrase: str) -> None:
    intent = IntentRecognizer().recognize(phrase)

    assert intent.action == "system.get_time"
    assert intent.parameters == {}
    assert intent.original_text == phrase
