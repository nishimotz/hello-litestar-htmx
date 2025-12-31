"""CSRF保護のテスト

テスト駆動開発（TDD）アプローチでCSRF保護の動作を確認します。
"""

import pytest
from litestar.testing import TestClient

from hello_litestar_htmx.app import app


@pytest.fixture
def client():
    """Provide a test client for the application."""
    with TestClient(app=app) as test_client:
        yield test_client


class TestCSRFProtection:
    """CSRF保護のテストスイート"""

    def test_get_request_sets_csrf_cookie(self, client):
        """GETリクエストでCSRFトークンがCookieに設定されることを確認"""
        response = client.get("/todos")
        assert response.status_code == 200
        
        # CSRFトークンがCookieに設定されていることを確認
        csrf_cookie = response.cookies.get("csrf_token")
        assert csrf_cookie is not None
        assert len(csrf_cookie) > 0

    def test_get_request_rotates_invalid_csrf_cookie(self, client):
        """無効なCSRF CookieがGETでローテーションされることを確認"""
        client.cookies.set("csrf_token", "invalid_token")

        response = client.get("/todos")
        assert response.status_code == 200

        csrf_cookie = response.cookies.get("csrf_token")
        assert csrf_cookie is not None
        assert csrf_cookie != "invalid_token"

    def test_post_with_valid_csrf_token_in_header_succeeds(self, client):
        """有効なCSRFトークンをヘッダーに含めたPOSTリクエストが成功することを確認"""
        # まずGETリクエストでCSRFトークンを取得
        get_response = client.get("/todos")
        assert get_response.status_code == 200
        
        csrf_token = get_response.cookies.get("csrf_token")
        assert csrf_token is not None
        
        # CSRFトークンをヘッダーに含めてPOSTリクエストを送信
        response = client.post(
            "/todos",
            data={"title": "CSRFテスト"},
            headers={
                "Content-Type": "application/x-www-form-urlencoded",
                "x-csrftoken": csrf_token,
            },
        )
        assert response.status_code == 201
        assert "CSRFテスト" in response.text

    def test_post_with_valid_csrf_token_in_form_succeeds(self, client):
        """有効なCSRFトークンをフォームデータに含めたPOSTリクエストが成功することを確認"""
        # まずGETリクエストでCSRFトークンを取得
        get_response = client.get("/todos")
        assert get_response.status_code == 200
        
        csrf_token = get_response.cookies.get("csrf_token")
        assert csrf_token is not None
        
        # CSRFトークンをフォームデータに含めてPOSTリクエストを送信
        response = client.post(
            "/todos",
            data={
                "title": "CSRFテスト（フォーム）",
                "_csrf_token": csrf_token,
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        assert response.status_code == 201
        assert "CSRFテスト（フォーム）" in response.text

    def test_post_without_csrf_token_fails(self, client):
        """CSRFトークンを含まないPOSTリクエストが403エラーを返すことを確認"""
        response = client.post(
            "/todos",
            data={"title": "CSRFなしテスト"},
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        assert response.status_code == 403

    def test_post_with_invalid_csrf_token_fails(self, client):
        """無効なCSRFトークンをヘッダーに含めたPOSTリクエストが403エラーを返すことを確認"""
        response = client.post(
            "/todos",
            data={"title": "無効なCSRFテスト"},
            headers={
                "Content-Type": "application/x-www-form-urlencoded",
                "x-csrftoken": "invalid_token",
            },
        )
        assert response.status_code == 403

    def test_post_with_mismatched_csrf_token_fails(self, client):
        """Cookieと一致しないCSRFトークンをヘッダーに含めたPOSTリクエストが403エラーを返すことを確認"""
        # まずGETリクエストでCSRFトークンを取得
        get_response = client.get("/todos")
        assert get_response.status_code == 200
        
        csrf_token = get_response.cookies.get("csrf_token")
        assert csrf_token is not None
        
        # 別のクライアントセッションで別のCSRFトークンを取得
        # （TestClientはセッション間でCookieを共有するため、新しいクライアントを作成）
        with TestClient(app=app) as client2:
            get_response2 = client2.get("/todos")
            csrf_token2 = get_response2.cookies.get("csrf_token")
            
            # 最初のクライアントのCookieを保持しつつ、別のトークンをヘッダーに設定
            # （Cookieとヘッダーのトークンが一致しない）
            response = client.post(
                "/todos",
                data={"title": "不一致CSRFテスト"},
                headers={
                    "Content-Type": "application/x-www-form-urlencoded",
                    "x-csrftoken": csrf_token2,  # 別のセッションのトークン
                },
            )
            assert response.status_code == 403

    def test_safe_methods_do_not_require_csrf_token(self, client):
        """安全なHTTPメソッド（GET、HEAD、OPTIONS）はCSRFトークンを要求しないことを確認"""
        # GETリクエストはCSRFトークンなしで成功する
        response = client.get("/todos")
        assert response.status_code == 200
        
        # OPTIONSリクエストもCSRFトークンなしで成功する
        # （HEADはルートハンドラがサポートしていないため、OPTIONSをテスト）
        # 204 No Contentは正常なレスポンス（CSRFエラーではない）
        response = client.options("/todos")
        assert response.status_code in [200, 204, 405]  # 204は正常、405はメソッドがサポートされていない場合
