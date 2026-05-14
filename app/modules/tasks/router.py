from http import HTTPStatus

from django.http import HttpRequest, HttpResponse
from ninja import Router

from app.modules.tasks.models import TaskStatus
from app.modules.tasks.schemas import CreateTaskSchema, TaskResponse, UpdateTaskSchema
from app.modules.tasks.service import TasksService
from app.shared.ratelimit import api_ratelimit

router = Router(tags=["tasks"])


@router.get("/", response=list[TaskResponse])
@api_ratelimit
def list_tasks(
    request: HttpRequest, status: TaskStatus | None = None, priority: int | None = None
) -> list[TaskResponse]:
    tasks = TasksService.find_all(status=status, priority=priority)
    return [TaskResponse.from_orm(t) for t in tasks]


@router.get("/{task_id}", response=TaskResponse)
@api_ratelimit
def get_task(request: HttpRequest, task_id: str) -> TaskResponse:
    task = TasksService.find_one(task_id)
    return TaskResponse.from_orm(task)


@router.post("/", response={HTTPStatus.CREATED: TaskResponse})
@api_ratelimit
def create_task(request: HttpRequest, data: CreateTaskSchema) -> TaskResponse:
    task = TasksService.create(data)
    return TaskResponse.from_orm(task)


@router.patch("/{task_id}", response=TaskResponse)
@api_ratelimit
def update_task(request: HttpRequest, task_id: str, data: UpdateTaskSchema) -> TaskResponse:
    task = TasksService.update(task_id, data)
    return TaskResponse.from_orm(task)


@router.delete("/{task_id}", response={HTTPStatus.NO_CONTENT: None})
@api_ratelimit
def delete_task(request: HttpRequest, task_id: str) -> HttpResponse:
    TasksService.delete(task_id)
    return HttpResponse(status=204)
