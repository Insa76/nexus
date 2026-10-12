from planner.decision import DecisionEngine
from planner.intent import Intent


def test_engine_decision_layer_is_available():
    engine = DecisionEngine()

    intent = Intent(
        action="system.open_app",
        confidence=0.95,
        parameters={
            "application": "Chrome",
        },
        original_text="Abrí Chrome",
    )

    decision = engine.decide(intent)

    assert decision.is_executable is True
    assert decision.selected_action == "system.open_app"


def test_unknown_intent_is_blocked():
    engine = DecisionEngine()

    intent = Intent(
        action="system.unknown",
        original_text="Hacé algo que no conozco",
    )

    decision = engine.decide(intent)

    assert decision.is_executable is False
    assert decision.selected_action is None


def test_decision_preserves_traceability():
    engine = DecisionEngine()

    intent = Intent(
        action="system.set_volume",
        confidence=0.91,
        parameters={
            "level": 60,
        },
        original_text="Poné el volumen al 60",
    )

    decision = engine.decide(
        intent,
        context={
            "last_request": "subí el volumen",
        },
    )

    assert decision.decision_id
    assert decision.reason
    assert decision.confidence == 0.91
    assert decision.metadata["status"] == "selected"


def test_decision_never_executes_an_action():
    engine = DecisionEngine()

    execution_happened = False

    intent = Intent(
        action="system.open_app",
        confidence=1.0,
        parameters={
            "application": "Chrome",
        },
        original_text="Abrí Chrome",
    )

    decision = engine.decide(intent)

    assert decision.is_executable is True
    assert execution_happened is False


def test_decision_respects_capabilities():
    engine = DecisionEngine()

    intent = Intent(
        action="system.open_app",
        confidence=0.9,
        parameters={
            "application": "Chrome",
        },
        original_text="Abrí Chrome",
    )

    capabilities = [
        {
            "name": "windows.set_volume",
            "action": "system.set_volume",
        }
    ]

    decision = engine.decide(
        intent,
        capabilities=capabilities,
    )

    assert decision.is_executable is False
    assert decision.selected_action is None
    assert decision.metadata["status"] == "unavailable"


def test_compound_decision_preserves_available_actions():
    engine = DecisionEngine()

    first = Intent(
        action="system.open_app",
        confidence=0.9,
        parameters={
            "application": "Chrome",
        },
        original_text="Abrí Chrome",
    )

    second = Intent(
        action="system.set_volume",
        confidence=0.9,
        parameters={
            "level": 50,
        },
        original_text="poné el volumen al 50",
    )

    compound = Intent(
        action="compound",
        confidence=0.9,
        original_text=(
            "Abrí Chrome y poné el volumen al 50"
        ),
        sub_intents=[
            first,
            second,
        ],
    )

    capabilities = [
        {
            "name": "windows.open_app",
            "action": "system.open_app",
        },
        {
            "name": "windows.set_volume",
            "action": "system.set_volume",
        },
    ]

    decision = engine.decide(
        compound,
        capabilities=capabilities,
    )

    assert decision.is_executable is True
    assert decision.selected_action == "system.open_app"
    assert decision.alternatives == [
        "system.set_volume"
    ]


def test_compound_without_capabilities_is_blocked():
    engine = DecisionEngine()

    first = Intent(
        action="system.open_app",
        original_text="Abrí Chrome",
    )

    second = Intent(
        action="system.set_volume",
        original_text="poné el volumen al 50",
    )

    compound = Intent(
        action="compound",
        original_text=(
            "Abrí Chrome y poné el volumen al 50"
        ),
        sub_intents=[
            first,
            second,
        ],
    )

    capabilities = [
        {
            "name": "windows.capture_screen",
            "action": "system.screen_capture",
        }
    ]

    decision = engine.decide(
        compound,
        capabilities=capabilities,
    )

    assert decision.is_executable is False
    assert decision.selected_action is None


def test_decision_context_is_recorded():
    engine = DecisionEngine()

    intent = Intent(
        action="system.mute",
        confidence=0.87,
        original_text="Silenciá el audio",
    )

    decision = engine.decide(
        intent,
        context={
            "last_request": "subí el volumen",
        },
    )

    assert decision.metadata["context_available"] is True


if __name__ == "__main__":
    tests = [
        test_engine_decision_layer_is_available,
        test_unknown_intent_is_blocked,
        test_decision_preserves_traceability,
        test_decision_never_executes_an_action,
        test_decision_respects_capabilities,
        test_compound_decision_preserves_available_actions,
        test_compound_without_capabilities_is_blocked,
        test_decision_context_is_recorded,
    ]

    for test in tests:
        test()

    print(
        f"ENGINE DECISION INTEGRATION PASSED : "
        f"{len(tests)} FAILED : 0"
    )
