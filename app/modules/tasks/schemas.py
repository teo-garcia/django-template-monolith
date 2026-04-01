from datetime import datetime
from uuid import UUID

from pydantic import Field
from ninja import Schema

from app.modules.tasks.models import TaskStatus


class CreateTaskSchema(Schema):
    title: str = Field(..., min_length=1, max_length=255)
    description: str = Field(default="", max_length=2000)
    status: TaskStatus = TaskStatus.PENDING
    priority: int = Field(default=0, ge=0, le=10)


class UpdateTaskSchema(Schema):
    title: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=2000)
    status: TaskStatus | None = None
    priority: int | None = Field(default=None, ge=0, le=10)


class TaskResponse(Schema):
    id: UUID
    title: str
    description: str
    status: str
    priority: int
    created_at: datetime
    updated_at: datetime
