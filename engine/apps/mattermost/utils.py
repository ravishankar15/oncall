def get_populate_mattermost_channel_task_id_key(organization_pk) -> str:
    return f"MATTERMOST_CHANNELS_TASK_ID_ORGANIZATION_{organization_pk}"
