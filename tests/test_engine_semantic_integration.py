from __future__ import annotations

from memory.semantic_memory import SemanticMemory
from memory.semantic_knowledge_extractor import (
    SemanticKnowledgeExtractor,
)
from memory.semantic_retriever import SemanticRetriever


def test_semantic_components_work_together() -> None:
    semantic_memory = SemanticMemory()

    extractor = SemanticKnowledgeExtractor(
        semantic_memory
    )

    retriever = SemanticRetriever(
        semantic_memory
    )

    from memory.episode import Episode

    episode = Episode(
        action="system.open_app",
        parameters={
            "application": "Chrome",
        },
        original_text="abrí chrome",
        success=True,
        output={
            "status": "opened",
            "application": "Chrome",
        },
    )

    facts = extractor.extract(
        episode
    )

    assert len(facts) == 1

    results = retriever.search(
        "chrome"
    )

    assert len(results) == 1

    match = results[0]

    assert match.fact.subject == "chrome"
    assert (
        match.fact.predicate
        == "es una aplicación"
    )
    assert match.fact.value is True


def test_failed_episode_does_not_create_knowledge() -> None:
    semantic_memory = SemanticMemory()

    extractor = SemanticKnowledgeExtractor(
        semantic_memory
    )

    from memory.episode import Episode

    episode = Episode(
        action="system.open_app",
        parameters={
            "application": "Chrome",
        },
        original_text="abrí chrome",
        success=False,
        output={},
    )

    facts = extractor.extract(
        episode
    )

    assert facts == []
    assert semantic_memory.count() == 0


def test_semantic_memory_is_reusable() -> None:
    semantic_memory = SemanticMemory()

    extractor = SemanticKnowledgeExtractor(
        semantic_memory
    )

    retriever = SemanticRetriever(
        semantic_memory
    )

    from memory.episode import Episode

    extractor.extract(
        Episode(
            action="system.open_app",
            parameters={
                "application": "Chrome",
            },
            original_text="abrí chrome",
            success=True,
            output={
                "status": "opened",
                "application": "Chrome",
            },
        )
    )

    first = retriever.search(
        "chrome"
    )

    second = retriever.search_by_subject(
        "chrome"
    )

    assert len(first) == 1
    assert len(second) == 1

    assert (
        first[0].fact
        is second[0].fact
    )


if __name__ == "__main__":
    tests = [
        test_semantic_components_work_together,
        test_failed_episode_does_not_create_knowledge,
        test_semantic_memory_is_reusable,
    ]

    passed = 0

    for test in tests:
        test()
        passed += 1

    print("=" * 72)
    print("ENGINE + SEMANTIC MEMORY INTEGRATION")
    print("=" * 72)
    print(f"PASSED : {passed}")
    print(f"FAILED : {len(tests) - passed}")
    print("=" * 72)
