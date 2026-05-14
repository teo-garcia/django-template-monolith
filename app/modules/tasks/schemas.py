from datetime import datetime
from uuid import UUID

from ninja import Schema
from pydantic import Field

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


class PaginationMeta(Schema):
    total: int = Field(..., ge=0)
    page: int = Field(..., ge=1)
    pageSize: int = Field(..., ge=1, le=100)  # noqa: N815


class TaskListResponse(Schema):
    data: list[TaskResponse]
    meta: PaginationMeta
