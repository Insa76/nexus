from __future__ import annotations

from memory.semantic_memory import SemanticMemory
from memory.semantic_retriever import SemanticRetriever


def test_search_by_subject() -> None:
    memory = SemanticMemory()

    memory.learn(
        "chrome",
        "es una aplicación",
        True,
    )

    memory.learn(
        "chrome",
        "plataforma",
        "windows",
    )

    retriever = SemanticRetriever(memory)

    results = retriever.search("chrome")

    assert len(results) == 2
    assert all(
        result.fact.subject == "chrome"
        for result in results
    )


def test_search_by_predicate() -> None:
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

    retriever = SemanticRetriever(memory)

    results = retriever.search("tipo")

    assert len(results) == 2


def test_search_by_value() -> None:
    memory = SemanticMemory()

    memory.learn(
        "chrome",
        "tipo",
        "browser",
    )

    retriever = SemanticRetriever(memory)

    results = retriever.search("browser")

    assert len(results) == 1
    assert results[0].fact.subject == "chrome"


def test_exact_subject_has_high_score() -> None:
    memory = SemanticMemory()

    memory.learn(
        "chrome",
        "tipo",
        "browser",
    )

    memory.learn(
        "chrome extension",
        "tipo",
        "browser",
    )

    retriever = SemanticRetriever(memory)

    results = retriever.search("chrome")

    assert results
    assert results[0].fact.subject == "chrome"


def test_search_by_subject_method() -> None:
    memory = SemanticMemory()

    memory.learn(
        "spotify",
        "tipo",
        "music",
    )

    memory.learn(
        "spotify",
        "plataforma",
        "windows",
    )

    retriever = SemanticRetriever(memory)

    results = retriever.search_by_subject(
        "Spotify"
    )

    assert len(results) == 2


def test_search_by_predicate_method() -> None:
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

    retriever = SemanticRetriever(memory)

    results = retriever.search_by_predicate(
        "Tipo"
    )

    assert len(results) == 2


def test_limit() -> None:
    memory = SemanticMemory()

    memory.learn("chrome", "a", True)
    memory.learn("chrome", "b", True)
    memory.learn("chrome", "c", True)

    retriever = SemanticRetriever(memory)

    results = retriever.search(
        "chrome",
        limit=2,
    )

    assert len(results) == 2


def test_empty_query() -> None:
    memory = SemanticMemory()

    memory.learn(
        "chrome",
        "tipo",
        "browser",
    )

    retriever = SemanticRetriever(memory)

    assert retriever.search("   ") == []


def test_no_match() -> None:
    memory = SemanticMemory()

    memory.learn(
        "chrome",
        "tipo",
        "browser",
    )

    retriever = SemanticRetriever(memory)

    assert retriever.search("notepad") == []


if __name__ == "__main__":
    tests = [
        test_search_by_subject,
        test_search_by_predicate,
        test_search_by_value,
        test_exact_subject_has_high_score,
        test_search_by_subject_method,
        test_search_by_predicate_method,
        test_limit,
        test_empty_query,
        test_no_match,
    ]

    passed = 0

    for test in tests:
        test()
        passed += 1

    print("=" * 72)
    print("SEMANTIC RETRIEVER")
    print("=" * 72)
    print(f"PASSED : {passed}")
    print(f"FAILED : {len(tests) - passed}")
    print("=" * 72)
