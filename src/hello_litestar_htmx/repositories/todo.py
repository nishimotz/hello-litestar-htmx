"""Todo repository for data access layer."""

from typing import Protocol

from hello_litestar_htmx.models.todo import Todo, TodoCreate, TodoUpdate


class TodoRepositoryProtocol(Protocol):
    """Protocol defining the interface for Todo repositories.

    This allows for easy mocking in tests and switching implementations (e.g., from in-memory to database).
    """

    def get_all(self) -> list[Todo]:
        """Get all todos."""
        ...

    def get_by_id(self, todo_id: int) -> Todo | None:
        """Get a todo by ID."""
        ...

    def create(self, todo_data: TodoCreate) -> Todo:
        """Create a new todo."""
        ...

    def update(self, todo_id: int, todo_data: TodoUpdate) -> Todo | None:
        """Update a todo. Returns None if not found."""
        ...

    def delete(self, todo_id: int) -> bool:
        """Delete a todo. Returns True if deleted, False if not found."""
        ...

    def toggle_completed(self, todo_id: int) -> Todo | None:
        """Toggle the completed status of a todo. Returns None if not found."""
        ...


class InMemoryTodoRepository:
    """In-memory implementation of TodoRepository.

    This is suitable for development and testing. In production, you would use
    a database-backed implementation (e.g., SQLAlchemy, Tortoise ORM).
    """

    def __init__(self) -> None:
        """Initialize the repository with empty storage."""
        self._todos: list[Todo] = []
        self._next_id: int = 1

    def get_all(self) -> list[Todo]:
        """Get all todos."""
        return self._todos.copy()

    def get_by_id(self, todo_id: int) -> Todo | None:
        """Get a todo by ID."""
        return next((t for t in self._todos if t.id == todo_id), None)

    def create(self, todo_data: TodoCreate) -> Todo:
        """Create a new todo."""
        todo = Todo(
            id=self._next_id,
            title=todo_data.title,
            completed=False,
        )
        self._todos.append(todo)
        self._next_id += 1
        return todo

    def update(self, todo_id: int, todo_data: TodoUpdate) -> Todo | None:
        """Update a todo. Returns None if not found."""
        todo = self.get_by_id(todo_id)
        if todo is None:
            return None

        # Update only provided fields
        if todo_data.title is not None:
            todo.title = todo_data.title
        if todo_data.completed is not None:
            todo.completed = todo_data.completed

        return todo

    def delete(self, todo_id: int) -> bool:
        """Delete a todo. Returns True if deleted, False if not found."""
        initial_length = len(self._todos)
        self._todos = [t for t in self._todos if t.id != todo_id]
        return len(self._todos) < initial_length

    def toggle_completed(self, todo_id: int) -> Todo | None:
        """Toggle the completed status of a todo. Returns None if not found."""
        todo = self.get_by_id(todo_id)
        if todo is None:
            return None

        todo.completed = not todo.completed
        return todo


# Type alias for dependency injection
TodoRepository = TodoRepositoryProtocol
