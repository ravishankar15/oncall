import logging

from rest_framework import mixins, status, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.api.permissions import RBACPermission
from apps.auth_token.auth import PluginAuthentication
from apps.mattermost.models import MattermostChannel
from apps.mattermost.serializers import MattermostChannelSerializer
from apps.mattermost.tasks import populate_mattermost_channels_for_organization
from common.api_helpers.mixins import PublicPrimaryKeyMixin
from common.insight_log.chatops_insight_logs import ChatOpsEvent, ChatOpsTypePlug, write_chatops_insight_log

logger = logging.getLogger(__name__)


class MattermostInstallViewSet(viewsets.GenericViewSet):
    authentication_classes = (PluginAuthentication,)
    permission_classes = (IsAuthenticated, RBACPermission)

    rbac_permissions = {
        "connect": [RBACPermission.Permissions.CHATOPS_UPDATE_SETTINGS],
        "disconnect": [RBACPermission.Permissions.CHATOPS_UPDATE_SETTINGS],
    }

    def connect(self, request):
        try:
            organization = request.user.organization
            if organization.mattermost_channels.exists():
                logger.error(f"Organization {organization.pk} already has mattermost integrated")
                return Response(status=status.HTTP_400_BAD_REQUEST)

            populate_mattermost_channels_for_organization.apply_async((self.request.user.organization.pk,))
        except Exception as e:
            logger.exception("Failed to connect mattermost e: %s", e)
            return Response({"error": "Something went wrong, try again later"}, 500)
        return Response(status=status.HTTP_201_CREATED)

    def disconnect(self, request):
        user = request.user
        organization = user.organization
        write_chatops_insight_log(
            author=user,
            event_name=ChatOpsEvent.WORKSPACE_DISCONNECTED,
            chatops_type=ChatOpsTypePlug.MATTERMOST.value,
        )
        organization.mattermost_channels.all().delete()
        return Response(status=status.HTTP_200_OK)


class MattermostChannelViewSet(
    PublicPrimaryKeyMixin[MattermostChannel],
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    authentication_classes = (PluginAuthentication,)
    permission_classes = (IsAuthenticated, RBACPermission)

    rbac_permissions = {
        "list": [RBACPermission.Permissions.CHATOPS_READ],
        "retrieve": [RBACPermission.Permissions.CHATOPS_READ],
        "reload": [RBACPermission.Permissions.CHATOPS_UPDATE_SETTINGS],
    }

    serializer_class = MattermostChannelSerializer

    def get_queryset(self):
        return MattermostChannel.objects.filter(organization=self.request.user.organization)
