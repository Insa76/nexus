from unittest.mock import MagicMock

from engine.cognitive_capabilities import CognitiveCapabilityRouter
from processes import ProcessCognitiveAccess


def test_engine_capability_catalog_contains_processes():
    process_access = MagicMock(
        spec=ProcessCognitiveAccess,
    )

    router = CognitiveCapabilityRouter(
        process_access=process_access,
    )

    operations = router.available_operations()

    capabilities = [
        {
            "action": operation.action,
            "capability": operation.capability,
            "operation": operation.operation,
            "type": "cognitive",
        }
        for operation in operations
    ]

    process_capability = next(
        item
        for item in capabilities
        if item["action"] == "processes.find_relevant"
    )

    assert process_capability == {
        "action": "processes.find_relevant",
        "capability": "processes",
        "operation": "find_relevant",
        "type": "cognitive",
    }
