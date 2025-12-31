"""CSRF helpers.

Litestar's `CSRFMiddleware` stores the active CSRF token in the connection state for
safe methods (GET/HEAD/OPTIONS), even on the very first request where the cookie
has not been set yet.

To make HTMX work on the initial page load (before a second request), templates
should use the token from state instead of only reading the request cookies.
"""

from __future__ import annotations

from litestar import Request
from litestar.utils.scope.state import ScopeState


def get_csrf_token(request: Request) -> str:
    """Return the CSRF token for the current request, if available."""
    state = ScopeState.from_scope(request.scope)
    token = getattr(state, "csrf_token", None)
    if token:
        return token
    return request.cookies.get("csrf_token", "")

