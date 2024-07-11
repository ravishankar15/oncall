import re
from typing import Tuple

from rest_framework import exceptions
from rest_framework.authentication import BaseAuthentication

from apps.mattermost.exceptions import MattermostTokenError
from apps.user_management.models import Organization

from .models import MattermostAuthToken


class MattermostAuthTokenAuthentication(BaseAuthentication):
    model = MattermostAuthToken

    def authenticate(self, request) -> Tuple[Organization, MattermostAuthToken]:
        print(request.META)
        auth = request.META.get('HTTP_MATTERMOST_APP_AUTHORIZATION')
        print(auth)
        if not auth:
            raise exceptions.AuthenticationFailed("Missing auth token")
        match_token = re.search(r"Bearer (\S+)", auth)
        if not match_token:
           raise exceptions.AuthenticationFailed("Invalid auth token")
        token = match_token.group(1)
        organization, auth_token = self.authenticate_credentials(token)
        return organization, auth_token

    def authenticate_credentials(self, token_string: str) -> Tuple[Organization, MattermostAuthToken]:
        try:
            auth_token = self.model.validate_token(token_string)
        except MattermostTokenError:
            raise exceptions.AuthenticationFailed("Invalid auth token")

        return auth_token.organization, auth_token
