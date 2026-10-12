from unittest.mock import MagicMock

from engine.cognitive_capabilities import CognitiveCapabilityRouter
from processes.cognitive import ProcessCognitiveAccess


def test_process_capability_router_exposes_process_operations():
    process_access = MagicMock(
        spec=ProcessCognitiveAccess,
    )

    router = CognitiveCapabilityRouter(
        process_access=process_access,
    )

    operations = router.available_operations()

    assert len(operations) == 3

    assert {
        (operation.capability, operation.operation, operation.action)
        for operation in operations
    } == {
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
    }
