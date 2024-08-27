from django.urls import include, path

from common.api_helpers.optional_slash_router import OptionalSlashRouter

from .views import MattermostChannelViewSet, MattermostInstallViewSet

app_name = "mattermost"
router = OptionalSlashRouter()
router.register(r"channels", MattermostChannelViewSet, basename="channel")

urlpatterns = [
    path("", include(router.urls)),
    path("connect", MattermostInstallViewSet.as_view({"post": "connect"}), name="connect"),
    path("disconnect", MattermostInstallViewSet.as_view({"post": "disconnect"}), name="disconnect"),
]
