import logging

from celery.utils.log import get_task_logger
from django.core.cache import cache

from apps.mattermost.client import MattermostClient
from apps.mattermost.utils import get_populate_mattermost_channel_task_id_key
from common.custom_celery_tasks import shared_dedicated_queue_retry_task

logger = get_task_logger(__name__)
logger.setLevel(logging.DEBUG)


@shared_dedicated_queue_retry_task(autoretry_for=(Exception,), retry_backoff=True, max_retries=None)
def populate_mattermost_channels_for_organization(organization_pk):
    from apps.mattermost.models import MattermostChannel
    from apps.user_management.models import Organization

    cache_key = get_populate_mattermost_channel_task_id_key(organization_pk=organization_pk)
    cache_task_id = cache.get(cache_key)
    current_task_id = populate_mattermost_channels_for_organization.request.id

    if cache_task_id:
        logger.info(
            f"Stop populate_mattermost_channels_for_organization for organization pk: {organization_pk} due to "
            f"duplicate task current_task_id: {current_task_id}; running_task_id: {cache_task_id}"
        )
        return

    cache.set(cache_key, current_task_id)

    organization = Organization.objects.get(pk=organization_pk)
    mc = MattermostClient()
    response = mc.get_public_channels()

    public_channels = {channel["channel_id"]: channel for channel in response}
    public_channel_ids = public_channels.keys()

    existing_channels = organization.mattermost_channels
    existing_channel_ids = set(existing_channels.values_list("channel_id", flat=True))

    # create existing channels
    channels_to_create = tuple(
        MattermostChannel(
            organization=organization, channel_id=channel["channel_id"], channel_name=channel["channel_name"]
        )
        for channel in public_channels.values()
        if channel["channel_id"] not in existing_channel_ids
    )
    MattermostChannel.objects.bulk_create(channels_to_create, batch_size=5000)

    # update existing channels
    channels_to_update = existing_channels.filter(channel_id__in=public_channels.keys())
    for channel in channels_to_update:
        public_channel = public_channels[channel.channel_id]
        channel.channel_name = public_channel["channel_name"]

    MattermostChannel.objects.bulk_update(channels_to_update, fields=("channel_name",), batch_size=5000)

    # delete excess channels
    channel_ids_to_delete = existing_channel_ids - public_channel_ids
    organization.mattermost_channels.filter(channel_id__in=channel_ids_to_delete).delete()

    cache.delete(cache_key)
