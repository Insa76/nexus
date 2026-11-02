from nexus_http_security import (
    cors_origin_for,
    is_allowed_browser_origin,
    is_allowed_content_length,
    is_allowed_host,
)


def test_allows_non_browser_clients_without_origin() -> None:
    assert is_allowed_browser_origin(None) is True
    assert cors_origin_for(None) is None


def test_allows_known_local_console_origins() -> None:
    for origin in (
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5174",
    ):
        assert is_allowed_browser_origin(origin) is True
        assert cors_origin_for(origin) == origin

def test_rejects_untrusted_browser_origins_and_null_origin() -> None:
    for origin in ("https://attacker.example", "null", "http://localhost:9000"):
        assert is_allowed_browser_origin(origin) is False
        assert cors_origin_for(origin) is None

def test_allows_only_loopback_hostnames_on_api_port() -> None:
    assert is_allowed_host("127.0.0.1:8765") is True
    assert is_allowed_host("localhost:8765") is True
    assert is_allowed_host("localhost") is True
    assert is_allowed_host("attacker.example:8765") is False
    assert is_allowed_host("localhost:9999") is False
    assert is_allowed_host("localhost:invalid") is False


def test_request_body_size_limit() -> None:
    assert is_allowed_content_length(1) is True
    assert is_allowed_content_length(1_048_576) is True
    assert is_allowed_content_length(0) is False
    assert is_allowed_content_length(-1) is False
    assert is_allowed_content_length(1_048_577) is False
