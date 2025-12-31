"""Routes for Todo operations."""

from typing import Annotated

from litestar import Request, Router, delete, get, post
from litestar.enums import RequestEncodingType
from litestar.params import Body
from litestar.response import Template
from litestar.status_codes import HTTP_200_OK, HTTP_201_CREATED
from pydantic import ValidationError

from hello_litestar_htmx.models.todo import TodoCreate
from hello_litestar_htmx.services.todo import TodoService


@get("/todos")
async def get_todos_page(request: Request, todo_service: TodoService) -> Template:
    """Todoリストページ

    通常アクセス: フルページ (todos.html)
    HTMXアクセス: 部分HTML (todos_partial.html)

    Args:
        request: The HTTP request object.
        todo_service: Injected TodoService instance.

    Returns:
        Template response with appropriate template based on request type.
    """
    todos = todo_service.get_all_todos()
    context = {"todos": todos}

    # HTMXリクエストかどうかを HX-Request ヘッダーで判定
    is_htmx = request.headers.get("HX-Request") == "true"

    if is_htmx:
        # HTMXリクエストの場合は部分HTMLだけを返す
        return Template(
            template_name="todos_partial.html",
            context=context
        )

    # 通常アクセスの場合はフルページを返す
    return Template(
        template_name="todos.html",
        context=context
    )


@post("/todos")
async def add_todo(
    data: Annotated[dict, Body(media_type=RequestEncodingType.URL_ENCODED)],
    todo_service: TodoService,
) -> Template:
    """Todo追加

    Args:
        data: Form data containing the todo title.
        todo_service: Injected TodoService instance.

    Returns:
        Template response with the new todo item or error message.
    """
    try:
        # Pydantic validation will automatically strip and validate
        todo_data = TodoCreate(title=data.get("title", ""))
        todo = todo_service.create_todo(todo_data)

        return Template(
            template_name="todo_item.html",
            context={"todo": todo},
            status_code=HTTP_201_CREATED,
        )
    except ValidationError as e:
        # Extract first error message
        error_msg = e.errors()[0]["msg"] if e.errors() else "入力エラー"
        return Template(
            template_name="todo_error.html",
            context={"error": error_msg},
            status_code=HTTP_200_OK,  # Validation error returns 200 with error message
        )


@post("/todos/{todo_id:int}/toggle")
async def toggle_todo(todo_id: int, todo_service: TodoService) -> Template:
    """Todo完了/未完了をトグル

    Args:
        todo_id: The ID of the todo to toggle.
        todo_service: Injected TodoService instance.

    Returns:
        Template response with the updated todo item.
    """
    todo = todo_service.toggle_todo_completed(todo_id)

    return Template(
        template_name="todo_item.html",
        context={"todo": todo}
    )


@delete("/todos/{todo_id:int}", status_code=HTTP_200_OK)
async def delete_todo(todo_id: int, todo_service: TodoService) -> str:
    """Todo削除

    Args:
        todo_id: The ID of the todo to delete.
        todo_service: Injected TodoService instance.

    Returns:
        Empty string on successful deletion.
    """
    todo_service.delete_todo(todo_id)
    return ""  # 削除時は空文字列を返す


router = Router(
    path="",
    route_handlers=[get_todos_page, add_todo, toggle_todo, delete_todo],
)
