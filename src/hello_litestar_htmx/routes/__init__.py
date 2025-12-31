"""Route handlers for the application."""

from hello_litestar_htmx.routes.pages import router as pages_router
from hello_litestar_htmx.routes.todos import router as todos_router

__all__ = ["pages_router", "todos_router"]
