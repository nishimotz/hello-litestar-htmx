# 03. HTMXリクエスト検出 - 同じURLで異なるレスポンス

**学習日**: 2025年某日

## 学んだこと

### HTMX Request Detection パターンの実装

同じエンドポイント `/todos` で、リクエストの種類によって異なるレスポンスを返す仕組みを実装しました。これが AGENTS.md で言っていた「推しポイント」です。

## 実装の詳細

### 1. HTTPヘッダーによる判定

HTMXは全てのリクエストに自動的に `HX-Request: true` ヘッダーを追加します。

**通常のブラウザアクセス（リンククリック）:**
```
GET /todos HTTP/1.1
Host: localhost:8000
Accept: text/html
```

**HTMXによるアクセス（ボタンクリック）:**
```
GET /todos HTTP/1.1
Host: localhost:8000
Accept: text/html
HX-Request: true      ← HTMXが自動的に追加
```

### 2. サーバー側の実装

`app.py` の `get_todos()` 関数でヘッダーをチェック:

```python
@get("/todos")
async def get_todos(request: Request) -> Template:
    """Todoリストページ

    通常アクセス: フルページ (todos.html)
    HTMXアクセス: 部分HTML (todos_partial.html)
    """
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
```

### 3. テンプレートの使い分け

**todos.html（フルページ）:**
- `{% extends "base.html" %}` でベースレイアウトを継承
- `<html>`, `<head>`, `<body>` タグを含む完全なHTML
- ナビゲーション、スタイル、スクリプトすべて含む

**todos_partial.html（部分HTML）:**
- ベースレイアウトを継承**しない**
- Todo追加フォームとリストだけのHTMLフラグメント
- `<html>` タグなどは含まない

### 4. フロントエンドでの利用

`index.html` で両方の方法を提供:

```html
<!-- 通常のリンク: フルページをロードして画面遷移 -->
<a href="/todos">📝 Todoリスト（通常リンク）- フルページ遷移</a>

<!-- HTMXボタン: 部分HTMLだけを取得して #htmx-demo の中に挿入 -->
<button hx-get="/todos" hx-target="#htmx-demo" hx-swap="innerHTML">
    📝 Todoリスト（HTMXリンク）- 部分HTML読み込み
</button>

<div id="htmx-demo" class="container">
    <!-- ここに部分HTMLが読み込まれます -->
</div>
```

## このパターンのメリット

1. **エンドポイントの一元化**: `/todos` という1つのURLで両方のケースに対応
2. **段階的な導入が可能**: 既存のページ遷移を壊さずにHTMXを追加できる
3. **SEO対応**: 通常アクセスではフルHTMLが返るので検索エンジンも正常にクロール可能
4. **プログレッシブエンハンスメント**: JavaScriptが無効でもリンクをクリックすればフルページが表示される
5. **シンプルな実装**: 複雑なルーティングや別エンドポイントを用意する必要がない

## つまづいた点

### HTMXRequest を使おうとして失敗

最初、Litestar の `litestar.contrib.htmx.request.HTMXRequest` を使おうとしましたが、`NameError` が発生しました。

```python
# これは動かなかった
from litestar.contrib.htmx.request import HTMXRequest

@get("/todos")
async def get_todos(request: HTMXRequest) -> Template:
    if request.htmx:
        ...
```

**解決策**: 標準の `Request` を使い、手動で `HX-Request` ヘッダーをチェックする方法に変更しました。これでシンプルかつ確実に動作します。

## 発見したこと

### 1. ログでの確認方法

`tail -f` でログを見ると、同じURL `/todos` へのリクエストが複数回記録されます:

```
INFO:     127.0.0.1:52067 - "GET /todos HTTP/1.1" 200 OK
INFO:     127.0.0.1:52071 - "GET /todos HTTP/1.1" 200 OK
INFO:     127.0.0.1:52073 - "GET /todos HTTP/1.1" 200 OK
```

同じURLでも、ヘッダーの違いで異なるレスポンスを返しているのが分かります。

### 2. ブラウザの開発者ツールで確認

Network タブを開くと:
- 通常リンク: フルHTML（数KB）
- HTMXボタン: 部分HTML（数百バイト）

転送量が大幅に削減されているのが確認できます。

### 3. プログレッシブエンハンスメントの実例

JavaScriptを無効にしてテスト:
- 通常のリンクは動作する（フルページ遷移）
- HTMXボタンは動作しない（JavaScriptが必要）

でも、どちらの方法でも最終的にTodoリストにアクセスできるため、ユーザー体験が保証されます。

## 次のステップ

このパターンを理解したので、次は以下のような機能を試してみたい:

- 検索機能（`hx-trigger="keyup changed delay:500ms"` でデバウンス実装）
- インライン編集（クリックでテキストボックスに変更）
- 無限スクロール（`hx-trigger="revealed"` で自動読み込み）
- 楽観的UI（`hx-swap="outerHTML swap:1s"` でアニメーション）

---

## 理解度確認クイズ（全問正解済み）

自分で作成したクイズで理解度を確認しました:

1. **HTMXが追加するヘッダー**: `HX-Request: true` ✓
2. **サーバー側の判定方法**: `request.headers.get("HX-Request")` ✓
3. **テンプレートの違い**: `todos_partial.html` はベースレイアウトを継承しない ✓
4. **最大のメリット**: 段階的導入とプログレッシブエンハンスメント ✓

---

**学習メモ**: この「同じエンドポイントで異なるレスポンス」パターンは、HTMX を使った開発の核心的な概念。RESTful な設計を保ちながら、モダンなSPA的なUXを実現できる。
