import pytest

from planner.intent_recognizer import IntentRecognizer


def test_recognizes_explicit_memory_write_and_preserves_value_case() -> None:
    intent = IntentRecognizer().recognize("Recordá que mi proyecto actual se llama NEXUS.")
    assert intent.action == "system.remember_fact"
    assert intent.parameters == {
        "subject": "user",
        "predicate": "proyecto actual",
        "value": "NEXUS",
    }


def test_recognizes_semantic_memory_lookup() -> None:
    intent = IntentRecognizer().recognize("¿Cómo se llama mi proyecto actual?")
    assert intent.action == "system.recall_fact"
    assert intent.parameters == {"subject": "user", "predicate": "proyecto actual"}


def test_recognizes_compound_remember_and_recall_last_fact() -> None:
    intent = IntentRecognizer().recognize(
        "Recordá que mi proyecto actual se llama NEXUS y después decime qué nombre te pedí recordar"
    )
    assert intent.is_compound
    assert [part.action for part in intent.sub_intents] == [
        "system.remember_fact",
        "system.recall_last_fact",
    ]
    assert intent.sub_intents[0].parameters["value"] == "NEXUS"

@pytest.mark.parametrize(
    "phrase",
    [
        "¿Qué recordás sobre prueba de persistencia de nexus?",
        "¿Qué tenés registrado sobre prueba de persistencia de nexus?",
    ],
)
def test_recognizes_semantic_memory_lookup_by_topic(
    phrase: str,
) -> None:
    intent = IntentRecognizer().recognize(phrase)

    assert intent.action == "system.recall_fact"
    assert intent.parameters == {
        "subject": "user",
        "predicate": "prueba de persistencia de nexus",
    }


@pytest.mark.parametrize(
    "phrase, expected_predicate",
    [
        ("¿Cuál es mi proyecto actual?", "proyecto actual"),
        ("¿Cual es mi proyecto actual?", "proyecto actual"),
    ],
)
def test_recognizes_direct_personal_fact_lookup(
    phrase: str,
    expected_predicate: str,
) -> None:
    intent = IntentRecognizer().recognize(phrase)

    assert intent.action == "system.recall_fact"
    assert intent.parameters == {
        "subject": "user",
        "predicate": expected_predicate,
    }


@pytest.mark.parametrize(
    "phrase",
    [
        "¿Qué recordás sobre mí?",
        "¿Qué recordás sobre mi persona?",
        "¿Qué tenés registrado sobre mí?",
    ],
)
def test_recognizes_broad_personal_memory_lookup(phrase: str) -> None:
    intent = IntentRecognizer().recognize(phrase)

    assert intent.action == "system.recall_fact"
    assert intent.parameters == {
        "subject": "user",
        "predicate": "__all__",
    }

