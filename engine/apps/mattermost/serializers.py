from rest_framework import serializers

from apps.mattermost.models import MattermostChannel


class MattermostChannelSerializer(serializers.ModelSerializer):
    id = serializers.CharField(read_only=True, source="public_primary_key")

    class Meta:
        model = MattermostChannel
        fields = [
            "id",
            "channel_id",
            "channel_name",
        ]
