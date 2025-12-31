"""Litestar + HTMX アプリケーションのメインファイル"""

from dataclasses import dataclass
from typing import Annotated

from litestar import Litestar, delete, get, post
from litestar.contrib.jinja import JinjaTemplateEngine
from litestar.enums import RequestEncodingType
from litestar.params import Body
from litestar.response import Template
from litestar.status_codes import HTTP_200_OK
from litestar.template.config import TemplateConfig


@dataclass
class Todo:
    """Todo項目"""
    id: int
    title: str
    completed: bool = False


# グローバルなTodoストレージ（本番環境ではDBを使用）
todos: list[Todo] = []
next_id: int = 1


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


@get("/todos")
async def get_todos() -> Template:
    """Todoリストページ"""
    return Template(
        template_name="todos.html",
        context={"todos": todos}
    )


@post("/todos")
async def add_todo(
    data: Annotated[dict, Body(media_type=RequestEncodingType.URL_ENCODED)]
) -> Template:
    """Todo追加"""
    global next_id

    title = data.get("title", "").strip()
    if not title:
        return Template(
            template_name="todo_error.html",
            context={"error": "タイトルを入力してください"}
        )

    todo = Todo(id=next_id, title=title)
    todos.append(todo)
    next_id += 1

    return Template(
        template_name="todo_item.html",
        context={"todo": todo}
    )


@post("/todos/{todo_id:int}/toggle")
async def toggle_todo(todo_id: int) -> Template:
    """Todo完了/未完了をトグル"""
    todo = next((t for t in todos if t.id == todo_id), None)
    if todo:
        todo.completed = not todo.completed

    return Template(
        template_name="todo_item.html",
        context={"todo": todo}
    )


@delete("/todos/{todo_id:int}", status_code=HTTP_200_OK)
async def delete_todo(todo_id: int) -> str:
    """Todo削除"""
    global todos
    todos = [t for t in todos if t.id != todo_id]
    return ""  # 削除時は空文字列を返す


app = Litestar(
    route_handlers=[index, hello, get_todos, add_todo, toggle_todo, delete_todo],
    template_config=TemplateConfig(
        directory="templates",
        engine=JinjaTemplateEngine,
    ),
)
