from bootstrap.bootstrap import build_engine
from engine.cognitive_capabilities import CognitiveCapabilityRouter


def test_bootstrap_injects_cognitive_capability_router_into_engine():
    engine = build_engine()

    router = engine.cognitive_capability_router

    assert isinstance(
        router,
        CognitiveCapabilityRouter,
    )

    assert router.document_access is engine.document_cognitive_access
    assert router.process_access is engine.process_cognitive_access
    assert router.rule_access is engine.rule_cognitive_access


def test_bootstrap_exposes_all_cognitive_capability_operations():
    engine = build_engine()

    router = engine.cognitive_capability_router

    assert router is not None

    operations = {
        (operation.capability, operation.operation, operation.action)
        for operation in router.available_operations()
    }

    assert operations == {
        (
            "documents",
            "find_relevant",
            "documents.find_relevant",
        ),
        (
            "processes",
            "find_relevant",
            "processes.find_relevant",
        ),
        (
            "processes",
            "get",
            "processes.get",
        ),
        (
            "processes",
            "list",
            "processes.list",
        ),
        (
            "rules",
            "find_relevant",
            "rules.find_relevant",
        ),
        (
            "rules",
            "get",
            "rules.get",
        ),
        (
            "rules",
            "list",
            "rules.list",
        ),
    }