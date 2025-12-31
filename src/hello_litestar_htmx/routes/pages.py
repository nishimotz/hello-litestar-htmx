"""Routes for static pages (index, hello, etc.)."""

from litestar import Router, get
from litestar.response import Template


@get("/")
async def index() -> Template:
    """トップページ"""
    return Template(template_name="index.html")


@get("/hello")
async def hello(name: str = "World") -> Template:
    """挨拶ページ - HTMXで動的に更新"""
    return Template(
        template_name="hello.html",
        context={"name": name}
    )


router = Router(
    path="",
    route_handlers=[index, hello],
)
