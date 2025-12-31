# 04. クリーンアーキテクチャー・型アノテーション・テスト

**学習日**: 2025年12月31日

## 学んだこと

アプリケーションを**レイヤードアーキテクチャ**にリファクタリングし、**Pydantic による型安全性**を導入し、**pytest による自動テスト**を追加しました。

## 実装したアーキテクチャ

### レイヤー構成

```
src/hello_litestar_htmx/
├── models/          # Pydanticモデル（データ定義層）
│   └── todo.py      # Todo, TodoCreate, TodoUpdate
├── repositories/    # データアクセス層
│   └── todo.py      # TodoRepository Protocol & InMemoryTodoRepository
├── services/        # ビジネスロジック層
│   └── todo.py      # TodoService
├── routes/          # プレゼンテーション層
│   ├── pages.py     # 静的ページ
│   └── todos.py     # Todo CRUD エンドポイント
└── app.py           # アプリケーション構成・DI設定
```

### 依存関係の流れ

```
Routes → Services → Repositories → Models
  ↓         ↓            ↓
DI      ビジネス     データ
注入    ロジック    アクセス
```

## 1. Models層 - Pydanticによる型安全なデータ定義

### models/todo.py

```python
from pydantic import BaseModel, Field, field_validator


class TodoBase(BaseModel):
    """共通フィールド"""
    title: str = Field(..., min_length=1, max_length=200)


class TodoCreate(TodoBase):
    """作成用スキーマ - バリデーション付き"""
    @field_validator("title")
    @classmethod
    def title_must_not_be_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("タイトルを入力してください")
        return v.strip()


class Todo(TodoBase):
    """完全なTodoモデル"""
    id: int
    completed: bool = False
```

**学んだポイント:**
- **Field()**でバリデーションルールを宣言的に定義
- **field_validator**で複雑なバリデーションロジック
- **自動的に型チェックとバリデーション**が実行される
- エラーメッセージは日本語でカスタマイズ可能

## 2. Repository層 - データアクセスの抽象化

### repositories/todo.py - Protocol パターン

```python
from typing import Protocol


class TodoRepositoryProtocol(Protocol):
    """リポジトリのインターフェース定義

    これにより:
    - テスト時にモックが簡単
    - 実装の切り替えが容易（InMemory → DB）
    - 依存性の逆転（DIP）を実現
    """
    def get_all(self) -> list[Todo]: ...
    def create(self, todo_data: TodoCreate) -> Todo: ...
    # ... その他のメソッド


class InMemoryTodoRepository:
    """インメモリ実装 - 開発/テスト用"""
    def __init__(self) -> None:
        self._todos: list[Todo] = []
        self._next_id: int = 1

    def create(self, todo_data: TodoCreate) -> Todo:
        todo = Todo(id=self._next_id, title=todo_data.title)
        self._todos.append(todo)
        self._next_id += 1
        return todo
```

**学んだポイント:**
- **Protocol**はダックタイピングの型ヒント版
- インターフェースを定義するが継承不要
- 将来的にSQLAlchemy/Tortoise ORMに置き換え可能
- **同じインターフェースで実装を切り替えられる**のがポイント

## 3. Service層 - ビジネスロジックの集約

### services/todo.py

```python
class TodoService:
    """ビジネスロジック層

    責務:
    - リポジトリの呼び出しをオーケストレーション
    - ビジネスルールの適用
    - 複数リポジトリにまたがる処理の調整
    """
    def __init__(self, repository: TodoRepository) -> None:
        self.repository = repository

    def create_todo(self, todo_data: TodoCreate) -> Todo:
        # Pydantic が自動的にバリデーション
        return self.repository.create(todo_data)
```

**学んだポイント:**
- **単一責任の原則**：ビジネスロジックだけを扱う
- Repositoryに依存するが、Protocolに依存（具象クラスではない）
- 将来的に複雑なビジネスルールを追加しやすい

## 4. Routes層 - プレゼンテーション

### routes/todos.py - 依存性注入

```python
@get("/todos")
async def get_todos_page(
    request: Request,
    todo_service: TodoService  # ← Litestarが自動注入
) -> Template:
    todos = todo_service.get_all_todos()
    # ... テンプレート返却
```

**ルーターの定義:**
```python
router = Router(
    path="",  # ← app.pyで"/todos"がプレフィックスされる
    route_handlers=[get_todos_page, add_todo, toggle_todo, delete_todo],
)
```

## 5. 依存性注入 (DI) の設定

### app.py

```python
from litestar.di import Provide

# グローバルインスタンス（アプリライフサイクル全体で共有）
_todo_repository = InMemoryTodoRepository()


def provide_todo_service() -> TodoService:
    """DIプロバイダー

    Litestarが自動的に呼び出してServiceを注入
    """
    return TodoService(_todo_repository)


app = Litestar(
    route_handlers=[pages_router, todos_router],
    dependencies={
        "todo_service": Provide(provide_todo_service, sync_to_thread=False),
    },
)
```

**学んだポイント:**
- **Provide()**で依存性を宣言
- **関数シグネチャの型ヒント**で自動的にマッチング
- `sync_to_thread=False`で async 関数と同期
- グローバル状態を一箇所で管理

## 6. テスト - pytest による自動テスト

### テスト構成

```
tests/
├── test_repositories.py  # Repository層の単体テスト
└── test_routes.py        # Routes層の統合テスト
```

### リポジトリのテスト（単体テスト）

```python
@pytest.fixture
def repository():
    """各テストに新しいリポジトリを提供"""
    return InMemoryTodoRepository()


def test_create_todo(repository):
    todo_data = TodoCreate(title="Test Todo")
    todo = repository.create(todo_data)

    assert todo.id == 1
    assert todo.title == "Test Todo"
    assert todo.completed is False
```

### ルートのテスト（統合テスト）

```python
from litestar.testing import TestClient


@pytest.fixture
def client():
    """テストクライアントを提供"""
    with TestClient(app=app) as test_client:
        yield test_client


def test_create_todo(client):
    response = client.post(
        "/todos",
        data={"title": "テスト用のTodo"},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert response.status_code == 200
    assert "テスト用のTodo" in response.text
```

**テスト実行結果:**
```
22 passed, 1 warning in 0.30s
```

### テストの分類 - ユニットテスト vs 統合テスト

#### test_repositories.py = ユニットテスト

- **テスト対象**: Repository層のみ
- **依存**: なし（fixtureで新規インスタンス）
- **速度**: 速い
- **目的**: データアクセスロジックの詳細な検証

```python
def test_create_todo(repository):
    """単一レイヤーのテスト"""
    todo_data = TodoCreate(title="Test Todo")
    todo = repository.create(todo_data)
    assert todo.id == 1
```

#### test_routes.py = 統合テスト

- **テスト対象**: Routes → Services → Repository → Templates の全層
- **依存**: TestClient（実際のHTTPリクエストをシミュレート）
- **速度**: 遅い
- **目的**: エンドツーエンドの動作確認

```python
def test_create_todo(client):
    """フルスタックのテスト"""
    response = client.post("/todos", data={"title": "テスト用のTodo"}, ...)
    assert response.status_code == 201       # HTTPステータスコード検証
    assert "テスト用のTodo" in response.text  # テンプレートレンダリング結果検証
    assert 'id="todo-1"' in response.text    # HTML構造検証
```

**統合テストで検証している内容**:

1. HTTPリクエスト全体のフロー（ルーティング、パース、バリデーション）
2. ビジネスロジックの実行
3. データ保存
4. テンプレートレンダリング
5. HTTPレスポンス（ステータスコード、HTML出力）

**HTMX特有のテスト**:

```python
def test_get_todos_htmx_request(client):
    """HTMXリクエストの振る舞いを検証"""
    response = client.get("/todos", headers={"HX-Request": "true"})
    assert "<html>" not in response.text.lower()  # Partial HTMLであることを確認
```

### テストでわかったこと

1. **Fixtureパターン**でテストデータを共有
2. **TestClient**でHTTPリクエストをシミュレート
3. **各テストが独立**（リポジトリが毎回新規作成）
4. **型チェックが効いている**ので実行時エラーが少ない
5. **test_routes.py は統合テスト**であり、テンプレートレンダリング結果とHTTPステータスコードの両方を検証する
6. **テストピラミッド**: ユニットテスト（多数、速い）→ 統合テスト（少数、遅い、包括的）

## つまづいた点

### 1. Pydantic のインストール

最初、`ModuleNotFoundError: No module named 'pydantic'` が発生。

**原因**: Litestar[standard]にPydanticが含まれると思ったが、別途インストール必要だった。

**解決**: `uv pip install pydantic`

### 2. Router の path 設定

最初、`Router(path="/todos")` としたため、ルートが `/todos/todos` になってしまった。

**原因**: app.pyで todos_router を登録する際に、既にプレフィックスが付く想定だった。

**解決**: `Router(path="")` に変更。app.pyでパスを制御。

### 3. テストのステータスコード - RESTful ベストプラクティス

POST /todos が 201 を返すべきだが、実際は 200 だった。

**原因**: Litestar の Template レスポンスは、デコレーターの `status_code` パラメータを無視する。Template 自体に `status_code` を指定する必要がある。

**試行錯誤**:

1. 最初の試み: `@post("/todos", status_code=HTTP_201_CREATED)` → 効果なし
2. 正しい方法: `Template(..., status_code=HTTP_201_CREATED)` → 成功

**解決**:

```python
@post("/todos")
async def add_todo(...) -> Template:
    try:
        todo = todo_service.create_todo(todo_data)
        return Template(
            template_name="todo_item.html",
            context={"todo": todo},
            status_code=HTTP_201_CREATED,  # ← RESTful ベストプラクティス
        )
    except ValidationError as e:
        return Template(
            template_name="todo_error.html",
            context={"error": error_msg},
            status_code=HTTP_200_OK,  # ← バリデーションエラーは 200
        )
```

**学んだこと**: RESTful API では、リソース作成成功時は **201 Created** を返すのがベストプラクティス。

## このアーキテクチャのメリット

### 1. テストしやすさ

- **Repository をモック化**して Service をテスト可能
- **Service をモック化**して Routes をテスト可能
- 各レイヤーが独立してテスト可能

### 2. 保守性

- **責務が明確**：どこに何を書くべきか迷わない
- **変更の影響範囲が限定的**：Repository を変更しても Routes は影響なし

### 3. 拡張性

- **データベース切り替えが容易**：InMemory → SQLAlchemy は Repository だけ変更
- **ビジネスロジック追加が容易**：Service に集中して記述
- **複数のフロントエンド対応**：Routes だけ追加（API/HTML/GraphQL）

### 4. 型安全性

- **Pydantic のバリデーション**で実行時エラーを防ぐ
- **型ヒント**で IDE の補完が効く
- **mypy などで静的型チェック**が可能

## 発見したこと

### 1. Protocol は継承不要の抽象化

従来の ABC (Abstract Base Class) と違い、Protocol は継承なしでインターフェースを定義できる。

```python
# ABC の場合（継承が必要）
class TodoRepository(ABC):
    @abstractmethod
    def create(self): ...

class InMemory(TodoRepository):  # 継承必須
    def create(self): ...


# Protocol の場合（継承不要）
class TodoRepositoryProtocol(Protocol):
    def create(self): ...

class InMemory:  # 継承不要、メソッドがあれば自動的に互換
    def create(self): ...
```

### 2. Litestar の DI は型ベース

関数の引数名と型で自動的にマッチング。Spring Boot の @Autowired に似ている。

### 3. Fixture は共有状態を防ぐ

各テストで新しいリポジトリを作ることで、テスト間の依存を排除できる。

## 次のステップ

このクリーンアーキテクチャを基盤に、次のような機能を追加できる:

- **SQLAlchemy でデータベース永続化**
- **認証・認可**（UserService, AuthService）
- **ページネーション**（Service で実装）
- **検索・フィルタ**（Repository で実装）
- **監査ログ**（Service でイベント記録）
- **キャッシング**（Repository でRedis導入）

---

**学習メモ**: クリーンアーキテクチャは最初は複雑に見えるが、プロジェクトが成長すると威力を発揮する。小規模プロジェクトでも、テストを書きやすくするために最低限のレイヤー分けは有効。
