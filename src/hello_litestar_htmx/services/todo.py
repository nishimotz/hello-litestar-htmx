"""Todo service for business logic layer."""

from hello_litestar_htmx.models.todo import Todo, TodoCreate, TodoUpdate
from hello_litestar_htmx.repositories.todo import TodoRepository


class TodoService:
    """Service layer for Todo business logic.

    This layer sits between the routes (presentation layer) and the repository (data layer).
    It contains business logic, validation, and orchestration of multiple repository calls.
    """

    def __init__(self, repository: TodoRepository) -> None:
        """Initialize the service with a repository.

        Args:
            repository: The Todo repository instance for data access.
        """
        self.repository = repository

    def get_all_todos(self) -> list[Todo]:
        """Get all todos.

        Returns:
            List of all Todo items.
        """
        return self.repository.get_all()

    def get_todo(self, todo_id: int) -> Todo | None:
        """Get a specific todo by ID.

        Args:
            todo_id: The ID of the todo to retrieve.

        Returns:
            The Todo item if found, None otherwise.
        """
        return self.repository.get_by_id(todo_id)

    def create_todo(self, todo_data: TodoCreate) -> Todo:
        """Create a new todo.

        Args:
            todo_data: The data for creating the todo.

        Returns:
            The newly created Todo item.

        Note:
            Validation is handled by Pydantic in the TodoCreate model.
        """
        return self.repository.create(todo_data)

    def update_todo(self, todo_id: int, todo_data: TodoUpdate) -> Todo | None:
        """Update an existing todo.

        Args:
            todo_id: The ID of the todo to update.
            todo_data: The updated data.

        Returns:
            The updated Todo item if found, None otherwise.
        """
        return self.repository.update(todo_id, todo_data)

    def delete_todo(self, todo_id: int) -> bool:
        """Delete a todo.

        Args:
            todo_id: The ID of the todo to delete.

        Returns:
            True if the todo was deleted, False if not found.
        """
        return self.repository.delete(todo_id)

    def toggle_todo_completed(self, todo_id: int) -> Todo | None:
        """Toggle the completed status of a todo.

        Args:
            todo_id: The ID of the todo to toggle.

        Returns:
            The updated Todo item if found, None otherwise.
        """
        return self.repository.toggle_completed(todo_id)
