from unittest.mock import MagicMock

from engine.cognitive_capabilities import (
    CognitiveCapabilityInvocation,
    CognitiveCapabilityRouter,
)


def test_cognitive_capability_invocation_is_recordable_in_memory():
    router = CognitiveCapabilityRouter(
        document_access=MagicMock(),
    )

    invocation = router.select(
        action="documents.find_relevant",
        parameters={
            "name": "manual.pdf",
        },
    )

    assert isinstance(
        invocation,
        CognitiveCapabilityInvocation,
    )

    memory = MagicMock()

    memory.add(
        "cognitive_capability",
        {
            "capability": invocation.capability,
            "operation": invocation.operation,
            "parameters": dict(
                invocation.parameters,
            ),
        },
    )

    memory.add.assert_called_once_with(
        "cognitive_capability",
        {
            "capability": "documents",
            "operation": "find_relevant",
            "parameters": {
                "name": "manual.pdf",
            },
        },
    )
