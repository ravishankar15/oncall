import logging
from typing import Optional

import requests
from requests.auth import AuthBase
from requests.models import PreparedRequest

from apps.base.utils import live_settings
from apps.mattermost.exceptions import MattermostAPITokenInvalid

logger = logging.getLogger(__name__)


class TokenAuth(AuthBase):
    def __init__(self, token: str) -> None:
        self.token = token

    def __call__(self, request: PreparedRequest) -> PreparedRequest:
        request.headers["Authorization"] = f"Bearer {self.token}"
        return request


class MattermostClient:
    def __init__(self, token: Optional[str] = None) -> None:
        self.token = token or live_settings.MATTERMOST_BOT_TOKEN
        self.base_url = f"{live_settings.MATTERMOST_HOST}/api/v4"
        self.timeout: int = 10

        if self.token is None:
            raise MattermostAPITokenInvalid

    def _paginated_request(self, path: str, per_page: int = 60) -> list:
        """
        This method does paginated api calls based on on page numbers.
        If the response length is not equal to per_page limit it means
        that we have fetched all the data.
        """
        page = 0
        paginated_response = []

        while True:
            data = []
            try:
                response = requests.get(
                    f"{self.base_url}/{path}",
                    params={"page": page, "per_page": per_page},
                    timeout=self.timeout,
                    auth=TokenAuth(self.token),
                )
                data = response.json()
            except requests.Timeout:
                logger.warning(f"Timeout while paginating page: {page} for path: {path}")
                break
            except requests.exceptions.RequestException as e:
                logger.warning(f"RequestException while paginating page: {page} for path: {path} ex: {str(e)}.")
                break

            page += 1
            paginated_response += data

            if len(data) != per_page:
                break
        return paginated_response

    def get_public_channels(self) -> list:
        """
        Makes paginated api calls to mattermost channels endpoint

        Returns a dict of required channel information

        Note:
        type = "O" means public channels
        type = "P" means private channels
        """
        response = self._paginated_request("channels")
        public_channels = []
        for res in response:
            if res["type"] == "O":
                public_channels.append({"channel_id": res["id"], "channel_name": res["display_name"]})
        return public_channels
