from django.urls import path

from app.main import api

urlpatterns = [
    path("", api.urls),
]
