"""Litestar + HTMX アプリケーションのメインファイル

このファイルはリファクタリングされ、レイヤードアーキテクチャを採用しています:
- models/: Pydanticモデルで型安全なデータ定義
- repositories/: データアクセス層（現在はインメモリ、将来的にDBに変更可能）
- services/: ビジネスロジック層
- routes/: プレゼンテーション層（ルートハンドラ）
"""

import json
import os
import secrets
from pathlib import Path

from litestar import Litestar, Request, Response
from litestar.config.csrf import CSRFConfig
from litestar.contrib.jinja import JinjaTemplateEngine
from litestar.di import Provide
from litestar.exceptions import PermissionDeniedException
from litestar.middleware import DefineMiddleware
from litestar.template.config import TemplateConfig
from litestar.status_codes import HTTP_403_FORBIDDEN

from hello_litestar_htmx.repositories.todo import InMemoryTodoRepository
from hello_litestar_htmx.routes import pages_router, todos_router
from hello_litestar_htmx.services.todo import TodoService
from hello_litestar_htmx.middleware.csrf import RotatingCSRFMiddleware

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


def _get_csrf_secret() -> str:
    env_secret = os.environ.get("LITESTAR_CSRF_SECRET") or os.environ.get("CSRF_SECRET")
    if env_secret:
        return env_secret

    repo_root = Path(__file__).resolve().parents[2]
    state_dir = repo_root / ".litestar"
    state_dir.mkdir(parents=True, exist_ok=True)
    secret_path = state_dir / "csrf-secret"

    if secret_path.exists():
        return secret_path.read_text(encoding="utf-8").strip()

    secret = secrets.token_urlsafe(32)
    secret_path.write_text(secret, encoding="utf-8")
    return secret


# CSRF保護の設定
# 本番環境では環境変数から取得することを推奨
csrf_secret = (
    _get_csrf_secret()
)
csrf_config = CSRFConfig(
    secret=csrf_secret,
    cookie_name="csrf_token",
    cookie_secure=False,  # 開発環境ではFalse、本番ではTrue（HTTPS必須）
    cookie_httponly=True,
    cookie_samesite="lax",
    header_name="x-csrftoken",  # デフォルトと同じだが明示的に指定
)

def csrf_exception_handler(request: Request, exc: PermissionDeniedException) -> Response:
    """CSRF例外をハンドリングしてログに記録"""
    return Response(
        content=json.dumps({"status_code": 403, "detail": "CSRF token verification failed"}),
        status_code=HTTP_403_FORBIDDEN,
        media_type="application/json",
    )


app = Litestar(
    route_handlers=[pages_router, todos_router],
    template_config=TemplateConfig(
        directory="templates",
        engine=JinjaTemplateEngine,
    ),
    dependencies={
        "todo_service": Provide(provide_todo_service, sync_to_thread=False),
    },
    middleware=[DefineMiddleware(RotatingCSRFMiddleware, config=csrf_config)],
    exception_handlers={PermissionDeniedException: csrf_exception_handler},
)
