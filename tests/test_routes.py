"""Tests for route handlers."""

import pytest
from litestar import Litestar
from litestar.testing import TestClient

from hello_litestar_htmx.app import app


@pytest.fixture
def client():
    """Provide a test client for the application."""
    with TestClient(app=app) as test_client:
        yield test_client


class TestPageRoutes:
    """Test suite for page routes."""

    def test_index_page(self, client):
        """Test that the index page loads successfully."""
        response = client.get("/")
        assert response.status_code == 200
        assert "Litestar + HTMX" in response.text

    def test_hello_page_default(self, client):
        """Test hello page with default name."""
        response = client.get("/hello")
        assert response.status_code == 200
        assert "World" in response.text

    def test_hello_page_with_name(self, client):
        """Test hello page with custom name."""
        response = client.get("/hello?name=テスト")
        assert response.status_code == 200
        assert "テスト" in response.text


class TestTodoRoutes:
    """Test suite for todo routes."""

    def test_get_todos_full_page(self, client):
        """Test getting todos as full page (non-HTMX request)."""
        response = client.get("/todos")
        assert response.status_code == 200
        assert "Todoリスト" in response.text

    def test_get_todos_htmx_request(self, client):
        """Test getting todos as partial HTML (HTMX request)."""
        response = client.get("/todos", headers={"HX-Request": "true"})
        assert response.status_code == 200
        assert "新しいTodoを追加" in response.text
        # Partial template should not have full page structure
        assert "<html>" not in response.text.lower()

    def test_create_todo(self, client):
        """Test creating a new todo."""
        response = client.post(
            "/todos",
            data={"title": "テスト用のTodo"},
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        assert response.status_code == 201
        assert "テスト用のTodo" in response.text
        assert 'id="todo-1"' in response.text

    def test_create_todo_empty_title(self, client):
        """Test creating a todo with empty title (should fail)."""
        response = client.post(
            "/todos",
            data={"title": "   "},  # Only whitespace
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        # Should return error template
        assert "タイトルを入力してください" in response.text

    def test_toggle_todo(self, client):
        """Test toggling a todo's completion status."""
        # First create a todo
        create_response = client.post(
            "/todos",
            data={"title": "トグルテスト"},
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        assert create_response.status_code == 201

        # Toggle it to completed
        toggle_response = client.post("/todos/1/toggle")
        assert toggle_response.status_code == 200
        assert 'checked' in toggle_response.text

        # Toggle it back to incomplete
        toggle_again_response = client.post("/todos/1/toggle")
        assert toggle_again_response.status_code == 200
        assert 'checked' not in toggle_again_response.text

    def test_delete_todo(self, client):
        """Test deleting a todo."""
        # First create a todo
        create_response = client.post(
            "/todos",
            data={"title": "削除テスト"},
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        assert create_response.status_code == 201

        # Delete it
        delete_response = client.delete("/todos/1")
        assert delete_response.status_code == 200
        assert delete_response.text == ""

    def test_delete_nonexistent_todo(self, client):
        """Test deleting a todo that doesn't exist."""
        # Should not fail even if todo doesn't exist
        response = client.delete("/todos/999")
        assert response.status_code == 200
