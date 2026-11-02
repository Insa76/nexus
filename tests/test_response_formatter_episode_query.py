from __future__ import annotations

from runtime.execution_result import ExecutionResult
from response.formatter import ResponseFormatter


def test_format_open_app_episode_query() -> None:
    formatter = ResponseFormatter()

    result = ExecutionResult(
        success=True,
        message="",
        output={
            "episode_query_result": {
                "status": "found",
                "action": "system.open_app",
                "field": "application",
                "value": "chrome",
                "original_text": "Abrí Chrome",
            },
            "status": "found",
            "action": "system.open_app",
            "field": "application",
            "value": "chrome",
        },
    )

    response = formatter.format(result)

    assert response == (
        "La última aplicación que abriste fue chrome."
    )


def test_format_close_app_episode_query() -> None:
    formatter = ResponseFormatter()

    result = ExecutionResult(
        success=True,
        message="",
        output={
            "episode_query_result": {
                "status": "found",
                "action": "system.close_app",
                "field": "application",
                "value": "chrome",
                "original_text": "Cerrá Chrome",
            },
            "status": "found",
            "action": "system.close_app",
            "field": "application",
            "value": "chrome",
        },
    )

    response = formatter.format(result)

    assert response == (
        "La última aplicación que cerraste fue chrome."
    )


def test_format_set_volume_episode_query() -> None:
    formatter = ResponseFormatter()

    result = ExecutionResult(
        success=True,
        message="",
        output={
            "episode_query_result": {
                "status": "found",
                "action": "system.set_volume",
                "field": "level",
                "value": 30.0,
                "original_text": "Poné el volumen al 30%",
            },
            "status": "found",
            "action": "system.set_volume",
            "field": "level",
            "value": 30.0,
        },
    )

    response = formatter.format(result)

    assert response == (
        "El último volumen que pusiste fue 30%."
    )


def test_format_unknown_episode_query_action() -> None:
    formatter = ResponseFormatter()

    result = ExecutionResult(
        success=True,
        message="",
        output={
            "episode_query_result": {
                "status": "found",
                "action": "system.some_future_action",
                "field": "value",
                "value": "algo",
            }
        },
    )

    response = formatter.format(result)

    assert response == (
        "Encontré la información en la memoria, "
        "pero todavía no puedo expresarla "
        "de forma natural."
    )


def test_format_episode_query_not_found() -> None:
    formatter = ResponseFormatter()

    result = ExecutionResult(
        success=True,
        message="",
        output={
            "episode_query_result": {
                "status": "not_found",
                "action": "system.open_app",
                "field": "application",
                "value": None,
            }
        },
    )

    response = formatter.format(result)

    assert response == (
        "No encontré la información "
        "que buscabas en la memoria."
    )


if __name__ == "__main__":
    tests = [
        test_format_open_app_episode_query,
        test_format_close_app_episode_query,
        test_format_set_volume_episode_query,
        test_format_unknown_episode_query_action,
        test_format_episode_query_not_found,
    ]

    for test in tests:
        test()

    print(f"PASS: {len(tests)}/{len(tests)}")
from runtime.execution_result import ExecutionResult
from response.formatter import ResponseFormatter


def test_format_current_time() -> None:
    formatter = ResponseFormatter()
    result = ExecutionResult(
        success=True,
        message="",
        output={
            "status": "read",
            "time": "14:35",
        },
    )

    assert formatter.format(result) == "Son las 14:35."

def test_format_current_date_and_time() -> None:
    formatter = ResponseFormatter()
    result = ExecutionResult(
        success=True,
        message="",
        output={
            "status": "read",
            "date": "28/10/2026",
            "time": "14:35",
        },
    )

    assert formatter.format(result) == "Hoy es 28/10/2026 y son las 14:35."

