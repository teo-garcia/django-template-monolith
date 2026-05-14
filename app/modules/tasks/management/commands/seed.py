from django.core.management.base import BaseCommand

from app.modules.tasks.models import Task, TaskStatus

SEED_TASKS = [
    {
        "title": "Review onboarding checklist",
        "description": "Confirm the template health, docs, metrics, and task APIs.",
        "status": TaskStatus.PENDING,
        "priority": 3,
    },
    {
        "title": "Ship API contract polish",
        "description": "Validate pagination, errors, and OpenAPI schema examples.",
        "status": TaskStatus.IN_PROGRESS,
        "priority": 7,
    },
    {
        "title": "Archive completed setup",
        "description": "Keep a completed task available for filtering examples.",
        "status": TaskStatus.COMPLETED,
        "priority": 1,
    },
]


class Command(BaseCommand):
    help = "Seed deterministic sample tasks for local development."

    def handle(self, *args: object, **options: object) -> None:
        Task.objects.all().delete()
        Task.objects.bulk_create(Task(**task) for task in SEED_TASKS)
        self.stdout.write(self.style.SUCCESS(f"Seeded {len(SEED_TASKS)} tasks"))
