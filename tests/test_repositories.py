"""Tests for repository layer."""

import pytest

from hello_litestar_htmx.models.todo import TodoCreate, TodoUpdate
from hello_litestar_htmx.repositories.todo import InMemoryTodoRepository


@pytest.fixture
def repository():
    """Provide a fresh repository for each test."""
    return InMemoryTodoRepository()


class TestInMemoryTodoRepository:
    """Test suite for InMemoryTodoRepository."""

    def test_get_all_empty(self, repository):
        """Test getting all todos from empty repository."""
        todos = repository.get_all()
        assert todos == []

    def test_create_todo(self, repository):
        """Test creating a new todo."""
        todo_data = TodoCreate(title="Test Todo")
        todo = repository.create(todo_data)

        assert todo.id == 1
        assert todo.title == "Test Todo"
        assert todo.completed is False

    def test_create_multiple_todos(self, repository):
        """Test creating multiple todos with incrementing IDs."""
        todo1 = repository.create(TodoCreate(title="First"))
        todo2 = repository.create(TodoCreate(title="Second"))

        assert todo1.id == 1
        assert todo2.id == 2
        assert len(repository.get_all()) == 2

    def test_get_by_id(self, repository):
        """Test getting a todo by ID."""
        created = repository.create(TodoCreate(title="Find me"))
        found = repository.get_by_id(created.id)

        assert found is not None
        assert found.id == created.id
        assert found.title == "Find me"

    def test_get_by_id_not_found(self, repository):
        """Test getting a non-existent todo."""
        found = repository.get_by_id(999)
        assert found is None

    def test_update_todo(self, repository):
        """Test updating a todo."""
        todo = repository.create(TodoCreate(title="Original"))
        updated = repository.update(
            todo.id,
            TodoUpdate(title="Updated", completed=True)
        )

        assert updated is not None
        assert updated.title == "Updated"
        assert updated.completed is True

    def test_update_partial(self, repository):
        """Test partial update of a todo."""
        todo = repository.create(TodoCreate(title="Original"))
        updated = repository.update(todo.id, TodoUpdate(completed=True))

        assert updated is not None
        assert updated.title == "Original"  # Title unchanged
        assert updated.completed is True

    def test_update_not_found(self, repository):
        """Test updating a non-existent todo."""
        updated = repository.update(999, TodoUpdate(title="Not found"))
        assert updated is None

    def test_delete_todo(self, repository):
        """Test deleting a todo."""
        todo = repository.create(TodoCreate(title="Delete me"))
        result = repository.delete(todo.id)

        assert result is True
        assert repository.get_by_id(todo.id) is None
        assert len(repository.get_all()) == 0

    def test_delete_not_found(self, repository):
        """Test deleting a non-existent todo."""
        result = repository.delete(999)
        assert result is False

    def test_toggle_completed(self, repository):
        """Test toggling todo completion status."""
        todo = repository.create(TodoCreate(title="Toggle me"))

        # Toggle to completed
        toggled = repository.toggle_completed(todo.id)
        assert toggled is not None
        assert toggled.completed is True

        # Toggle back to not completed
        toggled_again = repository.toggle_completed(todo.id)
        assert toggled_again is not None
        assert toggled_again.completed is False

    def test_toggle_completed_not_found(self, repository):
        """Test toggling a non-existent todo."""
        toggled = repository.toggle_completed(999)
        assert toggled is None
