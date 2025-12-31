"""Routes for static pages (index, hello, etc.)."""

from litestar import Request, Router, get
from litestar.response import Template

from hello_litestar_htmx.csrf import get_csrf_token

@get("/")
async def index(request: Request) -> Template:
    """トップページ"""
    return Template(
        template_name="index.html",
        context={"csrf_token": get_csrf_token(request)}
    )


@get("/hello")
async def hello(request: Request, name: str = "World") -> Template:
    """挨拶ページ - HTMXで動的に更新"""
    return Template(
        template_name="hello.html",
        context={"name": name, "csrf_token": get_csrf_token(request)}
    )


router = Router(
    path="",
    route_handlers=[index, hello],
)
