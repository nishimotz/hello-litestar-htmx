"""CSRF middleware extensions.

Litestar's `CSRFMiddleware` does not validate an existing CSRF cookie on "safe"
methods (GET/HEAD/OPTIONS). If the app's CSRF secret changes (e.g. during reload
or between processes), an old cookie can stick around and cause all subsequent
unsafe requests to fail with 403 until the browser cookie is cleared.

This middleware validates the CSRF cookie on safe methods and rotates it if it's
invalid for the current secret.
"""

from __future__ import annotations

import hashlib
import hmac
from secrets import compare_digest

from litestar.middleware.csrf import CSRFMiddleware

CSRF_SECRET_BYTES = 32
CSRF_SECRET_LENGTH = CSRF_SECRET_BYTES * 2


def _generate_csrf_hash(token: str, secret: str) -> str:
    return hmac.new(secret.encode(), token.encode(), hashlib.sha256).hexdigest()


def _is_valid_csrf_token(token: str, secret: str) -> bool:
    if len(token) < CSRF_SECRET_LENGTH + 1:
        return False
    token_secret = token[:CSRF_SECRET_LENGTH]
    existing_hash = token[CSRF_SECRET_LENGTH:]
    expected_hash = _generate_csrf_hash(token=token_secret, secret=secret)
    return compare_digest(existing_hash, expected_hash)


class RotatingCSRFMiddleware(CSRFMiddleware):
    """CSRFMiddleware that rotates invalid cookies on safe methods."""

    async def __call__(self, scope, receive, send):  # type: ignore[override]
        if scope.get("type") == "http":
            request = scope["litestar_app"].request_class(scope=scope, receive=receive)
            csrf_cookie = request.cookies.get(self.config.cookie_name)
            if csrf_cookie and request.method in self.config.safe_methods:
                if not _is_valid_csrf_token(csrf_cookie, self.config.secret):
                    request.cookies.pop(self.config.cookie_name, None)
        return await super().__call__(scope, receive, send)

