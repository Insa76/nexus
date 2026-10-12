from unittest.mock import MagicMock

from context import AssistantContext
from memory import WorkingMemory
from planner.context_builder import ContextBuilder


def test_context_builder_includes_context_provider_output():
    assistant_context = MagicMock(spec=AssistantContext)
    assistant_context.to_dict.return_value = {
        "user_id": "user-1",
        "organization_id": "org-1",
    }

    memory = WorkingMemory()

    captured = {}

    def provider(semantic_query, effective_assistant_context):
        captured["semantic_query"] = semantic_query
        captured["assistant_context"] = effective_assistant_context

        return {
            "documents": [
                {
                    "id": "doc-1",
                    "name": "manual.pdf",
                }
            ]
        }

    builder = ContextBuilder(
        assistant_context=assistant_context,
        context_providers=[provider],
    )

    result = builder.build(
        memory,
        semantic_query="buscar manual",
    )

    assert captured["semantic_query"] == "buscar manual"
    assert captured["assistant_context"] is assistant_context

    assert result["documents"] == [
        {
            "id": "doc-1",
            "name": "manual.pdf",
        }
    ]


def test_context_builder_ignores_provider_returning_none():
    memory = WorkingMemory()

    def provider(semantic_query, effective_assistant_context):
        return None

    builder = ContextBuilder(
        context_providers=[provider],
    )

    result = builder.build(
        memory,
        semantic_query="buscar algo",
    )

    assert "documents" not in result
