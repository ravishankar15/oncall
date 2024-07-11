import jwt
from typing import Tuple, Optional
from uuid import uuid4

from django.db import models, transaction

from apps.mattermost.utils import generate_jwt_rsa_keys, generate_mattermost_jwt_token, verify_mattermost_jwt_signature
from apps.mattermost.exceptions import MattermostTokenError
from apps.user_management.models import Organization, User


class MattermostAuthToken(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    secret = models.CharField(unique=True, editable=False, max_length=1024)

    actor = models.ForeignKey(
        "user_management.User",
        related_name="mattermost_auth_token_set",
        on_delete=models.CASCADE,
    )

    organization = models.OneToOneField(
        "user_management.Organization", on_delete=models.CASCADE, related_name="mattermost_auth_token"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    revoked_at = models.DateTimeField(null=True)

    @classmethod
    def create_auth_token(cls, user: User, organization: Organization) -> Tuple["MattermostAuthToken", str]:
        with transaction.atomic():
            public_key, private_key = generate_jwt_rsa_keys()
            instance = cls.objects.create(
                secret=public_key,
                actor=user,
                organization=organization,
            )
            token_string = generate_mattermost_jwt_token(kid=instance.uuid.hex, private_key=private_key)
        return instance, token_string

    @classmethod
    def validate_token(cls, token: str) -> Optional["MattermostAuthToken"]:
        try:
            print("Welcome to Auth")
            print(token)
            unverified_headers = jwt.get_unverified_header(token)
            print(unverified_headers)
            uuid = unverified_headers.get("kid")
            print(uuid)
            instance = MattermostAuthToken.objects.get(uuid=uuid)
            print(instance)
            verify_mattermost_jwt_signature(token=token, secret=instance.secret)
            return instance
        except (Exception) as e:
            print(e)
            raise MattermostTokenError

