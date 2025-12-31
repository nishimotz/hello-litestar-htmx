# 02. Todoリスト - CRUD操作

## 学習日時

2025-12-31

## 目標

Litestar + HTMX でCRUD操作（作成・読取・更新・削除）を実装し、動的UIの仕組みを理解する。

## 実装した機能

### 1. Todo追加（Create）
- フォームからPOSTリクエスト
- 空入力のバリデーション
- 新しいTodoを先頭に追加

### 2. Todo一覧表示（Read）
- サーバー起動時は空リスト
- Todoが追加されるたびに表示

### 3. 完了/未完了トグル（Update）
- チェックボックスでPOSTリクエスト
- 自分自身を置き換えて状態を更新

### 4. Todo削除（Delete）
- DELETEリクエストで削除
- 確認ダイアログ表示
- 要素をDOMから削除

## コードの重要ポイント

### 1. フォームデータの受け取り ([app.py:52-55](../src/hello_litestar_htmx/app.py#L52-L55))

```python
@post("/todos")
async def add_todo(
    data: Annotated[dict, Body(media_type=RequestEncodingType.URL_ENCODED)]
) -> Template:
```

**学んだこと**:
- HTMLフォームは `application/x-www-form-urlencoded` 形式
- `RequestEncodingType.URL_ENCODED` を明示しないとエラー
- これで `{"title": "やること"}` として受け取れる

**つまづいた点**:
- 最初 `Body()` だけで指定したら400 Bad Requestエラー
- ログを見て原因を特定し、media_typeを追加して解決

### 2. 部分HTMLテンプレートの返却 ([app.py:70-73](../src/hello_litestar_htmx/app.py#L70-L73))

```python
return Template(
    template_name="todo_item.html",
    context={"todo": todo}
)
```

**ポイント**:
- フルページではなく**HTMLの断片**だけを返す
- `todo_item.html` は1つのTodo項目の `<div>` だけ
- HTMXがこれを受け取り、指定した場所に挿入

### 3. HTMXの挿入位置制御 ([todos.html:11](../templates/todos.html#L11))

```html
<form hx-post="/todos" hx-target="#todo-list" hx-swap="afterbegin" hx-on::after-request="this.reset()">
```

**`hx-swap` の挙動**:
- `afterbegin` - 要素の**先頭**に追加（新しいTodoが一番上）
- `beforeend` - 要素の**末尾**に追加
- `innerHTML` - 要素の**内容を置き換え**（デフォルト）
- `outerHTML` - 要素**自体を置き換え**

**`hx-on::after-request`**:
- リクエスト完了後のイベント
- `this.reset()` でフォームをクリア
- JavaScriptは1行だけ

### 4. 自己更新パターン ([todo_item.html:3-9](../templates/todo_item.html#L3-L9))

```html
<input
    type="checkbox"
    hx-post="/todos/{{ todo.id }}/toggle"
    hx-target="#todo-{{ todo.id }}"
    hx-swap="outerHTML"
>
```

**動作フロー**:
1. チェックボックスをクリック
2. `/todos/1/toggle` にPOST
3. サーバーが更新された `todo_item.html` を返す
4. `hx-target="#todo-1"` で**自分自身**を指定
5. `hx-swap="outerHTML"` で**自分自身を置き換え**

**なぜ重要？**:
- 同じテンプレート（`todo_item.html`）を追加時とトグル時で再利用
- 状態の同期が自動的に行われる
- サーバーが常に正しいHTMLを生成

### 5. 削除時の空文字列 ([app.py:89-94](../src/hello_litestar_htmx/app.py#L89-L94))

```python
@delete("/todos/{todo_id:int}", status_code=HTTP_200_OK)
async def delete_todo(todo_id: int) -> str:
    global todos
    todos = [t for t in todos if t.id != todo_id]
    return ""  # 削除時は空文字列を返す
```

**ポイント**:
- `hx-swap="outerHTML"` で要素自体を置き換える
- 空文字列を返すと**要素が消える**
- `status_code=HTTP_200_OK` を明示（DELETEのデフォルト204では本文を返せない）

**つまづいた点**:
- 最初 `status_code` を指定せず、500エラー
- エラーメッセージを読んで200を明示して解決

### 6. データモデル ([app.py:15-20](../src/hello_litestar_htmx/app.py#L15-L20))

```python
@dataclass
class Todo:
    """Todo項目"""
    id: int
    title: str
    completed: bool = False

todos: list[Todo] = []
next_id: int = 1
```

**学んだこと**:
- `@dataclass` でシンプルなデータモデル定義
- グローバル変数でデータ管理（本番ではDB使用）
- `next_id` で一意なIDを生成

## 試したこと

1. ✅ Todo追加
   - 「買い物」「勉強」「運動」を追加
   - 新しいものが上に表示されることを確認

2. ✅ 完了トグル
   - 「買い物」をチェック → 取り消し線が表示
   - もう一度クリック → 取り消し線が消える
   - ページリロードなしで更新

3. ✅ 削除
   - 「運動」の削除ボタンをクリック
   - 確認ダイアログが表示
   - OKで要素が消える

4. ✅ バリデーション
   - 空のまま追加ボタンをクリック
   - 「タイトルを入力してください」エラー表示

5. ✅ ブラウザ開発者ツールで確認
   - Networkタブでリクエスト/レスポンス確認
   - レスポンスがHTMLの断片だけであることを確認
   - ページ全体のリロードがないことを確認

## 学んだこと

### Litestar について

1. **POSTハンドラーでのデータ受け取り**
   - `Body(media_type=RequestEncodingType.URL_ENCODED)` でフォームデータ
   - `Annotated[dict, Body(...)]` で型安全に受け取り

2. **DELETEハンドラーの戻り値**
   - デフォルトの204ステータスでは本文を返せない
   - `status_code=HTTP_200_OK` で明示的に200に設定

3. **テンプレートの再利用**
   - `todo_item.html` を追加・更新で共有
   - コンテキストに渡す `todo` オブジェクトだけ変える

### HTMX について

1. **JavaScriptほぼ不要**
   - HTML属性だけで動的UIを実現
   - `hx-*` 属性でサーバーとの通信を宣言的に記述

2. **部分HTML更新**
   - サーバーはHTML断片を返すだけ
   - フルページリロード不要でUX向上
   - ネットワーク転送量も削減

3. **自己更新パターンの威力**
   - `hx-target` で自分自身を指定
   - サーバーが常に正しい状態のHTMLを生成
   - クライアント側の状態管理が不要

4. **`hx-swap` の使い分け**
   - 追加: `afterbegin` で先頭に追加
   - 更新: `outerHTML` で自分自身を置き換え
   - 削除: 空文字列で要素を消す

5. **イベントハンドリング**
   - `hx-on::after-request` でリクエスト完了時の処理
   - 最小限のJavaScriptで実現

## 疑問点・調べたいこと

- [x] フォームデータの受け取り方 → `RequestEncodingType.URL_ENCODED` で解決
- [x] DELETEで空文字列を返す方法 → `status_code=HTTP_200_OK` で解決
- [ ] データベース連携（SQLite）の方法
- [ ] 同じエンドポイントでフルページ/部分HTMLを切り替える方法（HTMXリクエスト検知）
- [ ] より複雑なバリデーション（文字数制限など）
- [ ] `hx-trigger` の詳細な使い方（debounce、throttleなど）

## まとめ

**Litestar + HTMX の核心**:
1. サーバーは**HTMLの断片**だけを返す
2. HTMXが適切な場所に**自動挿入/置換/削除**
3. JavaScriptをほぼ書かずに**動的UI**を実現
4. サーバー側で状態管理 → シンプルで堅牢

**React/Vueとの違い**:
- JSON APIではなく、HTMLを返す
- クライアント側の状態管理が不要
- JavaScriptのビルドステップが不要
- サーバーサイドレンダリングが基本

## 次のステップ

- [ ] HTMXリクエストの検知と部分テンプレート返却
- [ ] データベース連携（SQLite）
- [ ] より高度なUI（インライン編集、検索機能）
- [ ] CSRF対策

## 参考リンク

- [Litestar Body Parameters](https://docs.litestar.dev/latest/usage/parameters.html#body-parameters)
- [HTMX Attributes](https://htmx.org/reference/#attributes)
- [HTMX hx-swap](https://htmx.org/attributes/hx-swap/)
- [HTMX Events](https://htmx.org/reference/#events)
