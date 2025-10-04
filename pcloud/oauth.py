# pcloud/oauth.py
from __future__ import annotations
from dataclasses import dataclass
from typing import Optional
from urllib.parse import urlencode
from ._http import EU_API, US_API, HTTP

@dataclass
class OAuthToken:
    access_token: str
    token_type: str = "bearer"

class PCloudOAuth2Flow:
    """
    OAuth2 (no-redirect) flow:
    - EU: https://e.pcloud.com
    - US: https://u.pcloud.com
    - We do NOT send redirect_uri. User copies the code shown on the page.
    """

    def __init__(self, app_key: str, app_secret: str, *, location: str = "EU") -> None:
        self.app_key = app_key
        self.app_secret = app_secret
        self.http = HTTP(base_url=EU_API if location.upper() == "EU" else US_API)

    def _authorize_base(self) -> str:
        return "https://e.pcloud.com" if self.http.base_url == EU_API else "https://u.pcloud.com"

    def start(
        self,
        *,
        state: Optional[str] = None,
        force_reapprove: bool = False,
        device_name: Optional[str] = None,
        prompt: Optional[str] = None,
    ) -> str:
        # Build URL without redirect_uri
        params = {"client_id": self.app_key, "response_type": "code"}
        if state:
            params["state"] = state
        if force_reapprove:
            params["force_reapprove"] = 1
        if device_name:
            params["device_name"] = device_name
        if prompt:
            params["prompt"] = prompt
        return f"{self._authorize_base()}/oauth2/authorize?{urlencode(params)}"

    def finish(self, code: str) -> OAuthToken:
        # Exchange code without redirect_uri
        payload = {
            "client_id": self.app_key,
            "client_secret": self.app_secret,
            "code": code,
            "grant_type": "authorization_code",
        }
        data = self.http.request("oauth2_token", payload, http_method="POST")
        token = data.get("access_token")
        if not token:
            raise RuntimeError("No access_token in OAuth response")
        return OAuthToken(access_token=token)

class PCloudOAuth2FlowNoRedirect(PCloudOAuth2Flow):
    pass
