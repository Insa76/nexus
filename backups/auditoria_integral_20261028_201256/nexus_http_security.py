"""Origin and Host validation for the local NEXUS HTTP API.

The API can execute local actions, so browser callers are restricted to the
known local development UIs. Non-browser clients without an Origin header
remain supported; Host is still restricted to loopback names.
"""
from __future__ import annotations

from urllib.parse import urlsplit

ALLOWED_BROWSER_ORIGINS = frozenset(
    {
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5174",
    }
)
ALLOWED_HOST_NAMES = frozenset({"localhost", "127.0.0.1"})
API_PORT = 8765
MAX_REQUEST_BODY_BYTES = 1_048_576  # 1 MiB por solicitud JSON


def is_allowed_browser_origin(origin: str | None) -> bool:
    """Allow non-browser clients and only the known local browser origins."""
    if origin is None or not origin.strip():
        return True
    return origin.strip() in ALLOWED_BROWSER_ORIGINS


def cors_origin_for(origin: str | None) -> str | None:
    """Return an origin to echo in CORS headers, never a wildcard."""
    if origin is None:
        return None
    normalized = origin.strip()
    return normalized if normalized in ALLOWED_BROWSER_ORIGINS else None


def is_allowed_host(host_header: str | None) -> bool:
    """Reject non-loopback Host headers (including DNS-rebinding domains)."""
    if host_header is None or not host_header.strip():
        # Preserve compatibility with HTTP/1.0 clients that omit Host.
        return True
    try:
        parsed = urlsplit("//" + host_header.strip())
        hostname = (parsed.hostname or "").lower()
        port = parsed.port
    except ValueError:
        return False
    return hostname in ALLOWED_HOST_NAMES and port in (None, API_PORT)


def is_allowed_content_length(content_length: int) -> bool:
    """Accept non-empty request bodies up to the configured safety limit."""
    return 0 < content_length <= MAX_REQUEST_BODY_BYTES
