# 05. CSRF対策（Litestar × HTMX）

**学習日**: 2025年12月31日

## 目的

- Todo追加/トグル/削除など **unsafe method**（POST/DELETE）をCSRF保護する
- HTMXのリクエストでも、毎回CSRFトークンが付くようにする
- `--reload`（複数プロセス）でも `403 Forbidden` で詰まらないようにする

## LitestarのCSRFの仕組み（要点）

- `CSRFMiddleware` がCSRF Cookie（このプロジェクトでは `csrf_token`）を発行する
- unsafe method では **Cookieのトークン** と **ヘッダー（`x-csrftoken`）またはフォーム（`_csrf_token`）** のトークンが一致しないと `403` になる
- フォーム送信（`application/x-www-form-urlencoded` / `multipart/form-data`）の場合、`_csrf_token` も自動で参照される

## HTMXでのトークン付与

このプロジェクトでは次の2段構えにしてあります（どちらでもOK）:

1) **HTMXヘッダー**（`x-csrftoken`）を自動付与  
`templates/base.html` の `<body>` に `hx-headers` を設定して、HTMXの全リクエストにヘッダーを乗せます。

2) **フォームhidden field**（`_csrf_token`）  
`templates/todos.html` と `templates/todos_partial.html` の `<form>` に hidden input を追加し、フォームとしても送れるようにします。

## 初回GETでトークンが空になる問題

最初のアクセスではまだCookieがセットされていないため、テンプレート側がCookieだけを見ると `csrf_token` が空になることがあります。

Litestarは safe method の処理中に **接続状態（ScopeState）** にCSRFトークンを保持しているため、テンプレートへ渡すトークンは cookie ではなく state を優先して取得します。

- `src/hello_litestar_htmx/csrf.py` の `get_csrf_token()` が `ScopeState.csrf_token` を優先して返す
- `src/hello_litestar_htmx/routes/pages.py` / `src/hello_litestar_htmx/routes/todos.py` はこのヘルパーを使う

## `--reload` で POST が403になる問題と対策

### 症状

`uvicorn --reload` で起動中に、`GET /todos` のあと `POST /todos` が `403` になることがありました。

### 原因（典型）

CSRF token の署名に使う **secret** がプロセスごとにズレると、Cookieに入っているトークンが別プロセスでは検証できず `403` になります。

### 対策

1) CSRF secret を固定する  
`src/hello_litestar_htmx/app.py` で次の優先順位にしています:

- 環境変数 `LITESTAR_CSRF_SECRET`（または `CSRF_SECRET`）
- 未設定の場合は `.litestar/csrf-secret` に自動保存した値

2) 古い/壊れたCSRF Cookieを自動で回復する（GET時）  
`src/hello_litestar_htmx/middleware/csrf.py` の `RotatingCSRFMiddleware` で、safe method のときにCookieが現在のsecretで検証できなければ破棄し、再発行されるようにしています。

これで「ブラウザのCookieを手で消さないと直らない」状態になりにくくなります。

## 起動コマンド例（uv）

```bash
export LITESTAR_CSRF_SECRET="change-me-to-a-long-random-string"
uv run python -m uvicorn src.hello_litestar_htmx.app:app --reload --host 127.0.0.1 --port 8000
```

## テスト

`tests/test_csrf.py` に基本的なケースに加えて、無効なCookieがGETでローテーションされるケースを追加しました。

