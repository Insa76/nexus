from planner.decision import DecisionEngine
from planner.intent import Intent


def test_known_action_without_capability_list():
    engine = DecisionEngine()

    intent = Intent(
        action="system.open_app",
        confidence=0.95,
        parameters={"application": "Chrome"},
        original_text="Abrí Chrome",
    )

    decision = engine.decide(intent)

    assert decision.selected_action == "system.open_app"
    assert decision.requires_execution is True
    assert decision.is_executable is True
    assert decision.confidence == 0.95


def test_unknown_intent_does_not_execute():
    engine = DecisionEngine()

    intent = Intent(
        action="system.unknown",
        original_text="Hacé algo",
    )

    decision = engine.decide(intent)

    assert decision.selected_action is None
    assert decision.requires_execution is False
    assert decision.is_executable is False
    assert decision.confidence == 0.0


def test_known_action_with_capabilities():
    engine = DecisionEngine()

    intent = Intent(
        action="system.set_volume",
        confidence=0.9,
        parameters={"level": 60},
        original_text="Poné el volumen al 60",
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

    assert decision.selected_action == "system.set_volume"
    assert decision.requires_execution is True
    assert decision.metadata["status"] == "selected"


def test_known_action_without_matching_capability():
    engine = DecisionEngine()

    intent = Intent(
        action="system.open_app",
        confidence=0.9,
        parameters={"application": "Chrome"},
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

    assert decision.selected_action is None
    assert decision.requires_execution is False
    assert decision.metadata["status"] == "unavailable"


def test_compound_intent_selects_first_available_action():
    engine = DecisionEngine()

    first = Intent(
        action="system.open_app",
        confidence=0.9,
        parameters={"application": "Chrome"},
        original_text="Abrí Chrome",
    )

    second = Intent(
        action="system.set_volume",
        confidence=0.9,
        parameters={"level": 50},
        original_text="poné el volumen al 50",
    )

    compound = Intent(
        action="compound",
        confidence=0.9,
        original_text="Abrí Chrome y poné el volumen al 50",
        sub_intents=[first, second],
    )

    capabilities = [
        {
            "name": "windows.set_volume",
            "action": "system.set_volume",
        }
    ]

    decision = engine.decide(
        compound,
        capabilities=capabilities,
    )

    assert decision.selected_action == "system.set_volume"
    assert decision.requires_execution is True
    assert decision.alternatives == []
    assert decision.metadata["compound"] is True


def test_compound_intent_keeps_alternatives():
    engine = DecisionEngine()

    first = Intent(
        action="system.open_app",
        confidence=0.9,
        original_text="Abrí Chrome",
    )

    second = Intent(
        action="system.set_volume",
        confidence=0.9,
        original_text="poné el volumen al 50",
    )

    compound = Intent(
        action="compound",
        confidence=0.9,
        original_text="Abrí Chrome y poné el volumen al 50",
        sub_intents=[first, second],
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

    assert decision.selected_action == "system.open_app"
    assert decision.alternatives == ["system.set_volume"]


def test_compound_without_available_actions_does_not_execute():
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
        original_text="Abrí Chrome y poné el volumen al 50",
        sub_intents=[first, second],
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

    assert decision.selected_action is None
    assert decision.requires_execution is False
    assert decision.metadata["status"] == "unavailable"


def test_decision_preserves_intent_and_context_metadata():
    engine = DecisionEngine()

    intent = Intent(
        action="system.mute",
        confidence=0.87,
        original_text="Silenciá el audio",
    )

    decision = engine.decide(
        intent,
        context={"last_request": "subí el volumen"},
    )

    assert decision.intent is intent
    assert decision.selected_action == "system.mute"
    assert decision.metadata["context_available"] is True
    assert decision.decision_id.startswith("decision-")


if __name__ == "__main__":
    tests = [
        test_known_action_without_capability_list,
        test_unknown_intent_does_not_execute,
        test_known_action_with_capabilities,
        test_known_action_without_matching_capability,
        test_compound_intent_selects_first_available_action,
        test_compound_intent_keeps_alternatives,
        test_compound_without_available_actions_does_not_execute,
        test_decision_preserves_intent_and_context_metadata,
    ]

    for test in tests:
        test()

    print(f"DECISION ENGINE PASSED : {len(tests)} FAILED : 0")
