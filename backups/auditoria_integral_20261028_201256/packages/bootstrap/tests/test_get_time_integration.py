import pytest

from bootstrap.bootstrap import build_engine


@pytest.mark.asyncio
async def test_engine_executes_get_time() -> None:
    engine = build_engine()

    result = await engine.execute("¿Qué hora es?")

    assert result.success, result.message
    assert isinstance(result.output, dict)
    assert result.output.get("status") == "read"
    assert isinstance(result.output.get("date"), str)
    assert len(result.output["date"]) == 10
    assert result.output["date"][2] == "/"
    assert isinstance(result.output.get("time"), str)
    assert len(result.output["time"]) == 5
    assert result.output["time"][2] == ":"
    assert result.metadata.get("response") == (
        f"Hoy es {result.output['date']} y son las {result.output['time']}."
    )
