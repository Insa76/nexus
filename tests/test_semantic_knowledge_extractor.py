from __future__ import annotations

from datetime import datetime, timezone

from memory.episode_memory import Episode
from memory.semantic_knowledge_extractor import (
    SemanticKnowledgeExtractor,
)
from memory.semantic_memory import SemanticMemory


def make_episode(
    *,
    action: str,
    parameters: dict | None = None,
    output: dict | None = None,
    success: bool = True,
) -> Episode:
    return Episode(
        action=action,
        parameters=parameters or {},
        original_text="test",
        success=success,
        output=output or {},
        timestamp=datetime.now(timezone.utc),
    )


def test_extract_open_app() -> None:
    memory = SemanticMemory()
    extractor = SemanticKnowledgeExtractor(memory)

    episode = make_episode(
        action="system.open_app",
        parameters={
            "application": "Chrome",
        },
    )

    facts = extractor.extract(episode)

    assert len(facts) == 1
    assert facts[0].subject == "chrome"
    assert facts[0].predicate == "es una aplicación"
    assert facts[0].value is True

    assert (
        memory.get_value(
            "chrome",
            "es una aplicación",
        )
        is True
    )


def test_extract_close_app() -> None:
    memory = SemanticMemory()
    extractor = SemanticKnowledgeExtractor(memory)

    episode = make_episode(
        action="system.close_app",
        parameters={
            "application": "Spotify",
        },
    )

    facts = extractor.extract(episode)

    assert len(facts) == 1
    assert facts[0].subject == "spotify"
    assert facts[0].predicate == "es una aplicación"


def test_extract_volume() -> None:
    memory = SemanticMemory()
    extractor = SemanticKnowledgeExtractor(memory)

    episode = make_episode(
        action="system.set_volume",
        parameters={
            "level": 60,
        },
    )

    facts = extractor.extract(episode)

    assert len(facts) == 1
    assert facts[0].subject == "system"
    assert facts[0].predicate == "último volumen conocido"
    assert facts[0].value == 60


def test_extract_volume_from_output() -> None:
    memory = SemanticMemory()
    extractor = SemanticKnowledgeExtractor(memory)

    episode = make_episode(
        action="system.set_volume",
        output={
            "level": 45,
        },
    )

    facts = extractor.extract(episode)

    assert len(facts) == 1
    assert facts[0].value == 45


def test_failed_episode_is_ignored() -> None:
    memory = SemanticMemory()
    extractor = SemanticKnowledgeExtractor(memory)

    episode = make_episode(
        action="system.open_app",
        parameters={
            "application": "Chrome",
        },
        success=False,
    )

    facts = extractor.extract(episode)

    assert facts == []
    assert memory.count() == 0


def test_unknown_action_is_ignored() -> None:
    memory = SemanticMemory()
    extractor = SemanticKnowledgeExtractor(memory)

    episode = make_episode(
        action="system.unknown_action",
        parameters={
            "application": "Chrome",
        },
    )

    facts = extractor.extract(episode)

    assert facts == []
    assert memory.count() == 0


def test_missing_application_is_ignored() -> None:
    memory = SemanticMemory()
    extractor = SemanticKnowledgeExtractor(memory)

    episode = make_episode(
        action="system.open_app",
        parameters={},
        output={},
    )

    facts = extractor.extract(episode)

    assert facts == []
    assert memory.count() == 0


def test_metadata_is_preserved() -> None:
    memory = SemanticMemory()
    extractor = SemanticKnowledgeExtractor(memory)

    episode = make_episode(
        action="system.open_app",
        parameters={
            "application": "Chrome",
        },
    )

    facts = extractor.extract(episode)

    assert facts[0].source == "episode"
    assert (
        facts[0].metadata["episode_action"]
        == "system.open_app"
    )

def test_invalid_volume_is_ignored() -> None:
    memory = SemanticMemory()
    extractor = SemanticKnowledgeExtractor(memory)

    episode = make_episode(
        action="system.set_volume",
        parameters={
            "level": "loud",
        },
    )

    facts = extractor.extract(episode)

    assert facts == []
    assert memory.count() == 0


def test_empty_application_is_ignored() -> None:
    memory = SemanticMemory()
    extractor = SemanticKnowledgeExtractor(memory)

    episode = make_episode(
        action="system.open_app",
        parameters={
            "application": "   ",
        },
    )

    facts = extractor.extract(episode)

    assert facts == []
    assert memory.count() == 0


def test_invalid_volume_from_output_is_ignored() -> None:
    memory = SemanticMemory()
    extractor = SemanticKnowledgeExtractor(memory)

    episode = make_episode(
        action="system.set_volume",
        output={
            "level": "unknown",
        },
    )

    facts = extractor.extract(episode)

    assert facts == []
    assert memory.count() == 0


def test_application_can_be_extracted_from_output() -> None:
    memory = SemanticMemory()
    extractor = SemanticKnowledgeExtractor(memory)

    episode = make_episode(
        action="system.open_app",
        output={
            "application": "Firefox",
        },
    )

    facts = extractor.extract(episode)

    assert len(facts) == 1
    assert facts[0].subject == "firefox"
    assert facts[0].predicate == "es una aplicación"
    assert facts[0].value is True


if __name__ == "__main__":
    tests = [
        test_extract_open_app,
        test_extract_close_app,
        test_extract_volume,
        test_extract_volume_from_output,
        test_failed_episode_is_ignored,
        test_unknown_action_is_ignored,
        test_missing_application_is_ignored,
        test_metadata_is_preserved,
    ]

    passed = 0

    for test in tests:
        test()
        passed += 1

    print("=" * 72)
    print("SEMANTIC KNOWLEDGE EXTRACTOR")
    print("=" * 72)
    print(f"PASSED : {passed}")
    print(f"FAILED : {len(tests) - passed}")
    print("=" * 72)
