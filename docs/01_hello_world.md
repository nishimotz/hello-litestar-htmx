# 01. Hello World アプリケーション

## 学習日時

2025-12-31

## 目標

Litestar + HTMX で最初の動的アプリケーションを作成し、基本的な仕組みを理解する。

## 実装したこと

### 1. プロジェクト構成

```
hello-litestar-htmx/
├── src/hello_litestar_htmx/
│   ├── __init__.py
│   └── app.py              # メインアプリケーション
├── templates/
│   ├── base.html           # ベーステンプレート
│   ├── index.html          # トップページ
│   └── hello.html          # 部分HTMLテンプレート
├── pyproject.toml
└── .gitignore
```

### 2. 主要なコード

#### app.py の構造

```python
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
```

**ポイント**:
- `@get("/")` デコレータでルーティング定義
- `Template` レスポンスでJinjaテンプレートを返す
- `context` でテンプレートに変数を渡す

#### HTMX の基本属性

[templates/index.html](../templates/index.html) で使用:

```html
<button
    hx-get="/hello"
    hx-include="#name-input"
    hx-target="#result"
    hx-vals='js:{name: document.getElementById("name-input").value}'
>
    挨拶する
</button>
```

**属性の意味**:
- `hx-get="/hello"` - ボタンクリック時に `/hello` へGETリクエスト
- `hx-vals` - リクエストパラメータを指定（JavaScriptで入力値を取得）
- `hx-target="#result"` - レスポンスHTMLを `#result` 要素に挿入
- ページ全体をリロードせず、**部分的にHTMLを更新**

### 3. サーバーの起動方法

```bash
# 仮想環境をアクティベート
source .venv/bin/activate

# 開発サーバー起動（自動リロード有効）
litestar --app src.hello_litestar_htmx.app:app run --reload
```

起動後、http://127.0.0.1:8000 でアクセス可能。

## 学んだこと

### Litestar について

1. **シンプルなルーティング**
   - デコレータベースで直感的
   - `@get`, `@post`, `@put`, `@delete` などHTTPメソッドごとに用意されている

2. **型ヒントの活用**
   - 関数の引数に型を指定すると、自動でバリデーション
   - `name: str = "World"` でクエリパラメータを受け取り、デフォルト値も設定可能

3. **テンプレートエンジン統合**
   - Jinja2が標準サポート
   - `TemplateConfig` で簡単に設定

### HTMX について

1. **JavaScriptほぼ不要**
   - HTML属性だけで動的UIを実現
   - `hx-*` 属性を追加するだけ

2. **部分HTML更新**
   - サーバーはHTML断片を返すだけ
   - フルページリロード不要でUX向上

3. **サーバーサイド中心**
   - ビジネスロジックは全てサーバー側
   - フロントエンドの複雑性が大幅に減少

## 試したこと

1. ✅ 名前を入力して「挨拶する」をクリック
   - 結果: "World たくや" さんへの挨拶が表示された

2. ✅ 異なる名前で再度クリック
   - 結果: "にしもつ" さんへの挨拶に更新された
   - ページリロードなしで部分更新を確認

3. ✅ ブラウザの開発者ツールでネットワークを確認
   - `/hello?name=にしもつ` へのGETリクエスト
   - レスポンスはHTMLの断片のみ（フルページではない）

## 疑問点・調べたいこと

- [ ] `hx-vals` 以外の方法で入力値を送る方法はある？
- [ ] POSTリクエストの場合はどう書く？
- [ ] エラーハンドリングはどうする？
- [ ] HTMX の他の属性（`hx-swap`, `hx-trigger` など）の使い方

## 次のステップ

- Todoリストを作ってCRUD操作を学ぶ
- POSTリクエストの扱い方
- データベース連携（SQLiteなど）

## 参考リンク

- [Litestar公式ドキュメント](https://litestar.dev/)
- [HTMX公式ドキュメント](https://htmx.org/)
- [Litestar HTMX Examples](https://github.com/litestar-org/htmx-examples-litestar)
