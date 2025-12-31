# Hello Litestar + HTMX

Litestar と HTMX を組み合わせたモダンなPythonウェブアプリケーションのサンプルリポジトリです。

## このリポジトリについて

このリポジトリは、**Litestar × HTMX ハンズオン勉強会**で実際に作成するサンプルアプリケーションです。JavaScriptを最小限に抑えながら、サーバーサイド中心で動的でレスポンシブなUIを実現します。

## 使用技術

### Litestar

高速で柔軟なPython ASGIフレームワーク。型ヒントをフル活用したクリーンな設計と、依存性注入が標準搭載で、大規模アプリにも最適です。

### HTMX

HTML属性だけでAJAX、WebSocket、部分更新を実現する軽量ライブラリ。React/Vueのような重いフロントエンドフレームワークなしで、動的でレスポンシブなUIをサーバーサイド中心に作れます。

### Litestar + HTMXの組み合わせ

- 公式にHTMXプラグインが統合されており、HTMXリクエストの検知や部分テンプレート返却が超簡単
- 同じエンドポイントで、通常アクセス時はフルページ、HTMX時は部分HTMLだけを返す、といったスマートな実装が可能
- JavaScriptをほとんど書かずに、現代的なインタラクティブアプリを作成

## 実装する機能

1. **Litestarの基本セットアップ**
   - プロジェクト構成
   - ルーティング設定
   - 依存性注入の活用

2. **Jinjaテンプレート + HTMXで動的UIの実装**
   - クリックでテーブル行追加/削除
   - インライン編集
   - 検索機能
   - Todoリストの実装

3. **実践的な機能**
   - CSRF対策
   - イベントトリガー
   - 部分テンプレート返却
   - エラーハンドリング

## セットアップ

### uv（推奨・最速）

[uv](https://github.com/astral-sh/uv)は超高速なPythonパッケージマネージャーです。従来のpipより10-100倍高速にインストールできます。

```bash
# uvのインストール（初回のみ）
curl -LsSf https://astral.sh/uv/install.sh | sh  # macOS/Linux
# Windows: irm https://astral.sh/uv/install.ps1 | iex

# プロジェクトのセットアップ（仮想環境作成+依存関係インストール）
uv venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
uv pip install -r requirements.txt

# アプリケーションの起動
litestar run
```

### 従来の方法（venv + pip）

```bash
# 仮想環境の作成
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 依存関係のインストール
pip install -r requirements.txt

# アプリケーションの起動
litestar run
```

## 参考リンク

- [Litestar公式サイト](https://litestar.dev/)
- [HTMX公式サイト](https://htmx.org/)
- [Litestar HTMXプラグイン](https://docs.litestar.dev/latest/usage/contrib/htmx.html)
- [Litestar HTMX Examples](https://github.com/litestar-org/htmx-examples-litestar)