from bootstrap.bootstrap import build_engine
from engine.cognitive_capabilities import CognitiveCapabilityRouter


def test_bootstrap_injects_cognitive_capability_router_into_engine():
    engine = build_engine()

    assert isinstance(
        engine.cognitive_capability_router,
        CognitiveCapabilityRouter,
    )

    assert (
        engine.cognitive_capability_router.document_access
        is engine.document_cognitive_access
    )
