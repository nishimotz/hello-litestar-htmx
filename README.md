# Hello Litestar + HTMX

Litestar と HTMX を学ぶための学習プロジェクト

## 🎯 このプロジェクトについて

このプロジェクトは、以下の技術を学ぶために作成しました：

- **Litestar**: 高速で型安全なPython Webフレームワーク
- **HTMX**: JavaScriptなしでインタラクティブなUIを実現
- **クリーンアーキテクチャ**: レイヤー分離による保守性の向上
- **Pydantic**: 型安全なデータバリデーション
- **pytest**: 自動テスト（ユニットテスト・統合テスト）

## 📚 学習記録

詳細な学習記録は [docs/](docs/) ディレクトリに保存されています：

- [docs/README.md](docs/README.md) - 目次
- [docs/01_hello_world.md](docs/01_hello_world.md) - 最初のアプリケーション
- [docs/02_todo_list.md](docs/02_todo_list.md) - TodoリストでCRUD操作を学ぶ
- [docs/03_htmx_detection.md](docs/03_htmx_detection.md) - HTMXリクエスト検出 - 同じURLで異なるレスポンス
- [docs/04_clean_architecture.md](docs/04_clean_architecture.md) - クリーンアーキテクチャー・型アノテーション・テスト
- [docs/05_csrf.md](docs/05_csrf.md) - CSRF対策（Litestar × HTMX）

## 🚀 クイックスタート

### 必要な環境

- Python 3.14
- uv (Pythonパッケージマネージャー)

### セットアップ

```bash
# リポジトリをクローン
git clone <repository-url>
cd hello-litestar-htmx

# 仮想環境を作成
uv venv

# 仮想環境を有効化
source .venv/bin/activate  # macOS/Linux
# または
.venv\Scripts\activate  # Windows

# 依存関係をインストール
uv pip install -e ".[dev]"
```

### サーバーを起動

```bash
litestar run --reload
```

複数ワーカーやリロード環境でCSRFの整合性を保つため、`LITESTAR_CSRF_SECRET`（または `CSRF_SECRET`）を固定値で設定することを推奨します（未設定の場合は `.litestar/csrf-secret` に自動保存されます）。

```bash
export LITESTAR_CSRF_SECRET="change-me-to-a-long-random-string"
litestar run --reload
```

ブラウザで http://127.0.0.1:8000 を開く

## 🧪 テストの実行

```bash
# 全テストを実行
pytest

# 詳細表示
pytest -v

# 特定のファイルのみ
pytest tests/test_routes.py

# バイトコード生成を抑制して実行
PYTHONDONTWRITEBYTECODE=1 pytest -v
```

## 🏗️ プロジェクト構造

```
hello-litestar-htmx/
├── src/
│   └── hello_litestar_htmx/
│       ├── models/          # Pydanticモデル（データ定義）
│       │   └── todo.py
│       ├── repositories/    # データアクセス層
│       │   └── todo.py
│       ├── services/        # ビジネスロジック層
│       │   └── todo.py
│       ├── routes/          # プレゼンテーション層（ルート）
│       │   ├── pages.py
│       │   └── todos.py
│       ├── templates/       # Jinja2テンプレート
│       │   ├── base.html
│       │   ├── index.html
│       │   ├── hello.html
│       │   ├── todos.html
│       │   ├── todos_partial.html
│       │   ├── todo_item.html
│       │   └── todo_error.html
│       ├── static/          # 静的ファイル（CSS）
│       │   └── style.css
│       └── app.py           # アプリケーションエントリーポイント
├── tests/                   # テストコード
│   ├── test_repositories.py # ユニットテスト
│   └── test_routes.py       # 統合テスト
├── docs/                    # 学習記録
└── pyproject.toml           # プロジェクト設定
```

## 🎨 実装した機能

### 1. Hello World (HTMX付き)

- `/` - トップページ
- `/hello?name=<名前>` - 挨拶ページ（HTMXでインタラクティブ）

### 2. Todo CRUD

- **作成**: フォームから新しいTodoを追加
- **読取**: Todoリストの表示
- **更新**: チェックボックスで完了/未完了をトグル
- **削除**: 削除ボタンでTodoを削除

すべての操作が**HTMX**により、ページ全体をリロードせずに実行されます。

## 🏛️ アーキテクチャ

### レイヤー構成

```
Routes (プレゼンテーション層)
  ↓ 依存性注入
Services (ビジネスロジック層)
  ↓
Repositories (データアクセス層)
  ↓
Models (データ定義層)
```

### 主要なパターン

- **Protocol パターン**: リポジトリの抽象化（継承不要のインターフェース）
- **依存性注入 (DI)**: Litestarの`Provide()`で自動注入
- **Pydantic バリデーション**: 型安全なデータ検証
- **Template パターン**: Jinja2によるHTMLレンダリング

## 🔧 VSCode デバッグ設定

[.vscode/launch.json](.vscode/launch.json) に以下の設定が含まれています：

- **Litestar: Run Server** - リロード付きでサーバー起動（F5）
- **Litestar: Run Server (No Reload)** - リロードなしで起動
- **Pytest: All Tests** - 全テストを実行
- **Pytest: Current File** - 現在のファイルのテストを実行

### デバッグの開始方法

1. VSCodeで **F5** を押す
2. または、サイドバーの **Run and Debug** (Ctrl+Shift+D) を開く
3. ドロップダウンから設定を選択して実行

## 📖 学んだこと

### Litestar

- 型ヒントベースの依存性注入
- Template レスポンスでのステータスコード指定
- Router によるルート管理
- TestClient による統合テスト

### HTMX

- `hx-get`, `hx-post`, `hx-delete` による非同期リクエスト
- `hx-target` でレスポンスの挿入先を指定
- `hx-swap` でDOM更新方法を制御
- `HX-Request` ヘッダーによるHTMXリクエストの判定

### クリーンアーキテクチャ

- レイヤー分離による責務の明確化
- Protocol による抽象化（テスト容易性の向上）
- 依存性の逆転原則 (DIP) の実践

### テスト

- **ユニットテスト** (test_repositories.py): 単一レイヤーの詳細なテスト
- **統合テスト** (test_routes.py): フルスタックのエンドツーエンドテスト
- pytest の Fixture パターン
- TestClient によるHTTPリクエストのシミュレーション

## ⚠️ つまづいた点と解決策

### 1. Pydantic のインストール

**問題**: `ModuleNotFoundError: No module named 'pydantic'`

**解決**: `uv pip install pydantic`（Litestar[standard] に含まれていない）

### 2. Router の path 設定

**問題**: `Router(path="/todos")` で `/todos/todos` になってしまった

**解決**: `Router(path="")` に変更（app.py でパスを制御）

### 3. RESTful ステータスコード

**問題**: POST が 200 を返してしまう

**解決**: `Template(..., status_code=HTTP_201_CREATED)` をレスポンスに指定

詳細は [docs/04_clean_architecture.md](docs/04_clean_architecture.md) を参照

## 🎓 次のステップ

- SQLAlchemy でデータベース永続化
- 認証・認可の実装
- ページネーション
- 検索・フィルタ機能
- 監査ログ
- キャッシング (Redis)

## 📝 ライセンス

学習用プロジェクトのため、ライセンスは未設定

## 🙏 謝辞

このプロジェクトは以下の技術を使用しています：

- [Litestar](https://litestar.dev/)
- [HTMX](https://htmx.org/)
- [Pydantic](https://docs.pydantic.dev/)
- [pytest](https://pytest.org/)
