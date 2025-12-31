"""Todo model definitions using Pydantic."""

from pydantic import BaseModel, Field, field_validator


class TodoBase(BaseModel):
    """Base Todo schema with common fields."""

    title: str = Field(..., min_length=1, max_length=200, description="Todo item title")


class TodoCreate(TodoBase):
    """Schema for creating a new Todo."""

    @field_validator("title")
    @classmethod
    def title_must_not_be_empty(cls, v: str) -> str:
        """Validate that title is not empty after stripping whitespace."""
        if not v.strip():
            raise ValueError("タイトルを入力してください")
        return v.strip()


class TodoUpdate(BaseModel):
    """Schema for updating a Todo."""

    title: str | None = Field(None, min_length=1, max_length=200)
    completed: bool | None = None

    @field_validator("title")
    @classmethod
    def title_must_not_be_empty(cls, v: str | None) -> str | None:
        """Validate that title is not empty after stripping whitespace."""
        if v is not None and not v.strip():
            raise ValueError("タイトルを入力してください")
        return v.strip() if v is not None else None


class Todo(TodoBase):
    """Todo model with all fields including database fields."""

    id: int = Field(..., description="Unique identifier")
    completed: bool = Field(default=False, description="Completion status")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "id": 1,
                    "title": "Litestarを学ぶ",
                    "completed": False,
                }
            ]
        }
    }
