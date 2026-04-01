from ninja import NinjaAPI

from app.config.env import get_settings
from app.modules.tasks.router import router as tasks_router
from app.shared.exceptions.handlers import register_exception_handlers

settings = get_settings()

api = NinjaAPI(
    title=settings.app_name,
    version=settings.app_version,
    docs_url="/docs",
)

register_exception_handlers(api)
api.add_router("/tasks", tasks_router)
