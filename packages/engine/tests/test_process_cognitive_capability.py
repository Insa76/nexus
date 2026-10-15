from unittest.mock import MagicMock

from context import AssistantContext

from processes import ProcessCognitiveAccess
from engine.cognitive_capabilities import (
    CognitiveCapabilityInvocation,
    CognitiveCapabilityRouter,
)


def test_router_invokes_process_cognitive_capability():
    process_access = MagicMock(
        spec=ProcessCognitiveAccess,
    )

    process_access.find_relevant.return_value = MagicMock()

    router = CognitiveCapabilityRouter(
        process_access=process_access,
    )

    invocation = CognitiveCapabilityInvocation(
        capability="processes",
        operation="find_relevant",
        parameters={},
    )

    context = AssistantContext(
        user=None,
        organization=None,
        projects=[],
    )

    result = router.invoke(
        invocation,
        context={},
        assistant_context=context,
    )

    assert result is process_access.find_relevant.return_value

    process_access.find_relevant.assert_called_once_with(
        context=context,
    )
