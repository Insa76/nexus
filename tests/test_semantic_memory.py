from __future__ import annotations

from memory.semantic_memory import SemanticMemory


def test_learn_and_get() -> None:
    memory = SemanticMemory()

    fact = memory.learn(
        "Chrome",
        "es una aplicación",
        True,
    )

    assert fact.subject == "chrome"
    assert fact.predicate == "es una aplicación"
    assert fact.value is True

    stored = memory.get(
        "chrome",
        "es una aplicación",
    )

    assert stored is fact


def test_get_value() -> None:
    memory = SemanticMemory()

    memory.learn(
        "chrome",
        "tipo",
        "browser",
    )

    assert (
        memory.get_value(
            "Chrome",
            "Tipo",
        )
        == "browser"
    )


def test_find_by_subject() -> None:
    memory = SemanticMemory()

    memory.learn(
        "chrome",
        "tipo",
        "browser",
    )

    memory.learn(
        "chrome",
        "plataforma",
        "windows",
    )

    facts = memory.find_by_subject(
        "chrome"
    )

    assert len(facts) == 2


def test_update_existing_fact() -> None:
    memory = SemanticMemory()

    first = memory.learn(
        "chrome",
        "tipo",
        "browser",
    )

    second = memory.learn(
        "chrome",
        "tipo",
        "application",
    )

    assert first is second
    assert memory.count() == 1
    assert (
        memory.get_value(
            "chrome",
            "tipo",
        )
        == "application"
    )


def test_find_by_predicate() -> None:
    memory = SemanticMemory()

    memory.learn(
        "chrome",
        "tipo",
        "browser",
    )

    memory.learn(
        "spotify",
        "tipo",
        "music",
    )

    facts = memory.find_by_predicate(
        "tipo"
    )

    assert len(facts) == 2


def test_forget() -> None:
    memory = SemanticMemory()

    memory.learn(
        "chrome",
        "tipo",
        "browser",
    )

    assert memory.forget(
        "chrome",
        "tipo",
    )

    assert memory.get(
        "chrome",
        "tipo",
    ) is None

    assert not memory.forget(
        "chrome",
        "tipo",
    )


def test_confidence_is_normalized() -> None:
    memory = SemanticMemory()

    low = memory.learn(
        "chrome",
        "confidence_test",
        True,
        confidence=-10,
    )

    high = memory.learn(
        "spotify",
        "confidence_test",
        True,
        confidence=10,
    )

    assert low.confidence == 0.0
    assert high.confidence == 1.0


def test_metadata_and_source() -> None:
    memory = SemanticMemory()

    fact = memory.learn(
        "chrome",
        "tipo",
        "browser",
        confidence=0.85,
        source="episode",
        metadata={
            "episode_action": "system.open_app",
        },
    )

    assert fact.confidence == 0.85
    assert fact.source == "episode"
    assert (
        fact.metadata["episode_action"]
        == "system.open_app"
    )


def test_clear() -> None:
    memory = SemanticMemory()

    memory.learn(
        "chrome",
        "tipo",
        "browser",
    )

    memory.learn(
        "spotify",
        "tipo",
        "music",
    )

    assert memory.count() == 2

    memory.clear()

    assert memory.count() == 0
    assert memory.all() == []


if __name__ == "__main__":
    tests = [
        test_learn_and_get,
        test_get_value,
        test_find_by_subject,
        test_update_existing_fact,
        test_find_by_predicate,
        test_forget,
        test_confidence_is_normalized,
        test_metadata_and_source,
        test_clear,
    ]

    passed = 0

    for test in tests:
        test()
        passed += 1

    print("=" * 72)
    print("SEMANTIC MEMORY")
    print("=" * 72)
    print(f"PASSED : {passed}")
    print(f"FAILED : {len(tests) - passed}")
    print("=" * 72)
