"""Litestar + HTMX アプリケーションのメインファイル"""

from litestar import Litestar, get
from litestar.response import Template
from litestar.contrib.jinja import JinjaTemplateEngine
from litestar.template.config import TemplateConfig


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


app = Litestar(
    route_handlers=[index, hello],
    template_config=TemplateConfig(
        directory="templates",
        engine=JinjaTemplateEngine,
    ),
)
