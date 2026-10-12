from __future__ import annotations

from memory import WorkingMemory
from memory.context_builder import ContextBuilder
from memory.semantic_memory import SemanticMemory
from memory.semantic_retriever import SemanticRetriever


def test_context_without_semantic_memory_is_compatible() -> None:
    memory = WorkingMemory()

    memory.add(
        "user_request",
        {
            "text": "abrí chrome",
        },
    )

    builder = ContextBuilder()

    context = builder.build(memory)

    assert context["last_request"] == {
        "text": "abrí chrome",
    }

    assert context["semantic_knowledge"] == []


def test_context_includes_semantic_knowledge() -> None:
    working_memory = WorkingMemory()

    semantic_memory = SemanticMemory()

    semantic_memory.learn(
        "chrome",
        "es una aplicación",
        True,
        confidence=1.0,
        source="episode",
    )

    retriever = SemanticRetriever(
        semantic_memory
    )

    builder = ContextBuilder(
        semantic_retriever=retriever
    )

    context = builder.build(
        working_memory,
        semantic_query="chrome",
    )

    knowledge = context[
        "semantic_knowledge"
    ]

    assert len(knowledge) == 1
    assert knowledge[0]["subject"] == "chrome"
    assert (
        knowledge[0]["predicate"]
        == "es una aplicación"
    )
    assert knowledge[0]["value"] is True
    assert knowledge[0]["confidence"] == 1.0
    assert knowledge[0]["source"] == "episode"


def test_semantic_knowledge_has_score() -> None:
    working_memory = WorkingMemory()

    semantic_memory = SemanticMemory()

    semantic_memory.learn(
        "spotify",
        "tipo",
        "music",
    )

    retriever = SemanticRetriever(
        semantic_memory
    )

    builder = ContextBuilder(
        semantic_retriever=retriever
    )

    context = builder.build(
        working_memory,
        semantic_query="spotify",
    )

    knowledge = context[
        "semantic_knowledge"
    ]

    assert len(knowledge) == 1
    assert knowledge[0]["score"] > 0


def test_empty_semantic_query_returns_empty() -> None:
    working_memory = WorkingMemory()

    semantic_memory = SemanticMemory()

    semantic_memory.learn(
        "chrome",
        "tipo",
        "browser",
    )

    retriever = SemanticRetriever(
        semantic_memory
    )

    builder = ContextBuilder(
        semantic_retriever=retriever
    )

    context = builder.build(
        working_memory,
        semantic_query="   ",
    )

    assert context[
        "semantic_knowledge"
    ] == []


def test_semantic_memory_does_not_change_references() -> None:
    working_memory = WorkingMemory()

    semantic_memory = SemanticMemory()

    semantic_memory.learn(
        "chrome",
        "es una aplicación",
        True,
    )

    retriever = SemanticRetriever(
        semantic_memory
    )

    builder = ContextBuilder(
        semantic_retriever=retriever
    )

    context = builder.build(
        working_memory,
        semantic_query="chrome",
    )

    assert context["references"] == {
        "last_action": None,
        "last_application": None,
        "last_executed_application": None,
        "last_volume": None,
        "previous_volume": None,
        "last_capture_available": False,
    }


if __name__ == "__main__":
    tests = [
        test_context_without_semantic_memory_is_compatible,
        test_context_includes_semantic_knowledge,
        test_semantic_knowledge_has_score,
        test_empty_semantic_query_returns_empty,
        test_semantic_memory_does_not_change_references,
    ]

    passed = 0

    for test in tests:
        test()
        passed += 1

    print("=" * 72)
    print("CONTEXT BUILDER + SEMANTIC MEMORY")
    print("=" * 72)
    print(f"PASSED : {passed}")
    print(f"FAILED : {len(tests) - passed}")
    print("=" * 72)
