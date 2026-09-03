from django.urls import path

from app.main import api

handler404 = "app.shared.exceptions.handlers.not_found_error_handler"

urlpatterns = [
    path("", api.urls),
]
