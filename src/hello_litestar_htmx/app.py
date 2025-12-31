"""Litestar + HTMX アプリケーションのメインファイル

このファイルはリファクタリングされ、レイヤードアーキテクチャを採用しています:
- models/: Pydanticモデルで型安全なデータ定義
- repositories/: データアクセス層（現在はインメモリ、将来的にDBに変更可能）
- services/: ビジネスロジック層
- routes/: プレゼンテーション層（ルートハンドラ）
"""

from litestar import Litestar
from litestar.contrib.jinja import JinjaTemplateEngine
from litestar.di import Provide
from litestar.template.config import TemplateConfig

from hello_litestar_htmx.repositories.todo import InMemoryTodoRepository
from hello_litestar_htmx.routes import pages_router, todos_router
from hello_litestar_htmx.services.todo import TodoService

# グローバルなリポジトリインスタンス
# 本番環境では、アプリケーション状態やDB接続プールを使用
_todo_repository = InMemoryTodoRepository()


def provide_todo_service() -> TodoService:
    """Dependency provider for TodoService.

    Litestarの依存性注入システムが自動的にこの関数を呼び出し、
    TodoServiceインスタンスをルートハンドラに注入します。

    Returns:
        TodoService instance with injected repository.
    """
    return TodoService(_todo_repository)


app = Litestar(
    route_handlers=[pages_router, todos_router],
    template_config=TemplateConfig(
        directory="templates",
        engine=JinjaTemplateEngine,
    ),
    dependencies={
        "todo_service": Provide(provide_todo_service, sync_to_thread=False),
    },
)
