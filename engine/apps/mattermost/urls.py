from django.urls import path

from .views import GetMattermostManifest, MattermostBindings, MattermostInstall

urlpatterns = [
    path("manifest", GetMattermostManifest.as_view()),
    path("install", MattermostInstall.as_view()),
    path("bindings", MattermostBindings.as_view()),
]
