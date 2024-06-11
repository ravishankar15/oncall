from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.mattermost.auth import MattermostAuthTokenAuthentication, MattermostWebhookAuthTokenAuthentication

MATTERMOST_CONNECTED_TEXT = (
    "Done! <b>{app_id}</b> Successfully Installed and Linked with organization <b>{organization_title} 🎉</b>"
)


class GetMattermostManifest(APIView):
    authentication_classes = (MattermostAuthTokenAuthentication,)

    def get(self, request):
        auth_token = request.query_params.get("auth_token")
        manifest = self._build_manifest(auth_token)
        return Response(manifest, status=status.HTTP_200_OK)

    def _build_on_install_callback(self, auth_token: str) -> dict:
        return {
            "path": "/mattermost/install",
            "expand": {"app": "summary", "acting_user": "summary"},
            "state": {"auth_token": auth_token},
        }

    def _build_bindings_callback(self, auth_token: str) -> dict:
        return {"path": "/mattermost/bindings", "state": {"auth_token": auth_token}}

    def _build_manifest(self, auth_token: str) -> dict:
        return {
            "app_id": "Grafana-Oncall",
            "version": "1.0.0",
            "display_name": "Grafana Oncall",
            "description": "Grafana Oncall app for sending and receiving events from mattermost",
            "homepage_url": "https://grafana.com/docs/oncall/latest/",
            "requested_permissions": ["act_as_bot"],
            "requested_locations": ["/in_post", "/post_menu", "/command"],
            "on_install": self._build_on_install_callback(auth_token=auth_token),
            "bindings": self._build_bindings_callback(auth_token=auth_token),
            "http": {"root_url": "http://host.docker.internal:8080"},
        }


class MattermostInstall(APIView):
    authentication_classes = (MattermostWebhookAuthTokenAuthentication,)

    def post(self, request):
        app_id = request.data.get("context").get("app").get("app_id")
        view_text = MATTERMOST_CONNECTED_TEXT.format(
            app_id=app_id, organization_title=request.auth.organization.org_title
        )
        # TODO: Create and save bot user and access token and also link org and user with mattermost
        response = {"type": "ok", "text": view_text}
        return Response(response, status=status.HTTP_200_OK)


class MattermostBindings(APIView):
    authentication_classes = (MattermostWebhookAuthTokenAuthentication,)

    def post(self, request):
        # TODO: Implement bindings or slash commands
        response = {"type": "ok"}
        return Response(response, status=status.HTTP_200_OK)
