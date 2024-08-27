from rest_framework import mixins, status, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.api.permissions import RBACPermission
from apps.auth_token.auth import PluginAuthentication
from apps.mattermost.models import MattermostChannel
from apps.mattermost.serializers import MattermostChannelSerializer
from common.api_helpers.mixins import PublicPrimaryKeyMixin


class MattermostInstallViewSet(viewsets.GenericViewSet):
    authentication_classes = (PluginAuthentication,)
    permission_classes = (IsAuthenticated, RBACPermission)

    rbac_permissions = {
        "connect": [RBACPermission.Permissions.CHATOPS_UPDATE_SETTINGS],
        "disconnect": [RBACPermission.Permissions.CHATOPS_UPDATE_SETTINGS],
    }

    def connect(self, request):
        return Response(status=status.HTTP_200_OK)

    def disconnect(self, request):
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
