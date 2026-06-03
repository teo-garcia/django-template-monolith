from http import HTTPStatus
from typing import Annotated

from django.http import HttpRequest, HttpResponse
from ninja import Query, Router, Status

from app.modules.tasks.models import TaskStatus
from app.modules.tasks.schemas import CreateTaskSchema, PaginationMeta, TaskListResponse, TaskResponse, UpdateTaskSchema
from app.modules.tasks.service import TasksService
from app.shared.exceptions.schemas import ErrorEnvelope
from app.shared.ratelimit import api_ratelimit

router = Router(tags=["tasks"])


@router.get("/", response={HTTPStatus.OK: TaskListResponse, HTTPStatus.UNPROCESSABLE_ENTITY: ErrorEnvelope})
@api_ratelimit
def list_tasks(
    request: HttpRequest,
    status: TaskStatus | None = None,
    priority: int | None = None,
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(alias="pageSize", ge=1, le=100)] = 20,
) -> TaskListResponse:
    tasks, total = TasksService.find_all(status=status, priority=priority, page=page, page_size=page_size)
    return TaskListResponse(
        data=[TaskResponse.from_orm(t) for t in tasks],
        meta=PaginationMeta(total=total, page=page, pageSize=page_size),
    )


@router.get("/{task_id}", response={HTTPStatus.OK: TaskResponse, HTTPStatus.NOT_FOUND: ErrorEnvelope})
@api_ratelimit
def get_task(request: HttpRequest, task_id: str) -> TaskResponse:
    task = TasksService.find_one(task_id)
    return TaskResponse.from_orm(task)


@router.post(
    "/",
    response={HTTPStatus.CREATED: TaskResponse, HTTPStatus.UNPROCESSABLE_ENTITY: ErrorEnvelope},
)
@api_ratelimit
def create_task(request: HttpRequest, data: CreateTaskSchema) -> Status[TaskResponse]:
    task = TasksService.create(data)
    return Status(HTTPStatus.CREATED, TaskResponse.from_orm(task))


@router.patch(
    "/{task_id}",
    response={
        HTTPStatus.OK: TaskResponse,
        HTTPStatus.NOT_FOUND: ErrorEnvelope,
        HTTPStatus.UNPROCESSABLE_ENTITY: ErrorEnvelope,
    },
)
@api_ratelimit
def update_task(request: HttpRequest, task_id: str, data: UpdateTaskSchema) -> TaskResponse:
    task = TasksService.update(task_id, data)
    return TaskResponse.from_orm(task)


@router.delete(
    "/{task_id}",
    response={HTTPStatus.NO_CONTENT: None, HTTPStatus.NOT_FOUND: ErrorEnvelope},
)
@api_ratelimit
def delete_task(request: HttpRequest, task_id: str) -> HttpResponse:
    TasksService.delete(task_id)
    return HttpResponse(status=204)
