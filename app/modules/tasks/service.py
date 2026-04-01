from ninja.errors import HttpError

from app.modules.tasks.models import Task, TaskStatus
from app.modules.tasks.schemas import CreateTaskSchema, UpdateTaskSchema


class TasksService:
    @staticmethod
    def find_all(status: TaskStatus | None = None, priority: int | None = None) -> list[Task]:
        query = Task.objects.all()

        if status is not None:
            query = query.filter(status=status)

        if priority is not None:
            query = query.filter(priority__gte=priority)

        return list(query)

    @staticmethod
    def find_one(task_id: str) -> Task:
        try:
            return Task.objects.get(pk=task_id)
        except Task.DoesNotExist as err:
            raise HttpError(404, "Task not found") from err

    @staticmethod
    def create(data: CreateTaskSchema) -> Task:
        return Task.objects.create(**data.dict())

    @staticmethod
    def update(task_id: str, data: UpdateTaskSchema) -> Task:
        task = TasksService.find_one(task_id)
        for field, value in data.dict(exclude_unset=True).items():
            setattr(task, field, value)
        task.save()
        return task

    @staticmethod
    def delete(task_id: str) -> None:
        task = TasksService.find_one(task_id)
        task.delete()
