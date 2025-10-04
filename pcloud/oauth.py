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
    """Web-app style OAuth flow with redirect URI."""
    def __init__(self, app_key: str, app_secret: str, redirect_uri: str, *, location: str = "EU") -> None:
        self.app_key = app_key
        self.app_secret = app_secret
        self.redirect_uri = redirect_uri
        self.http = HTTP(base_url=EU_API if location.upper() == "EU" else US_API)

    def start(self, *, state: Optional[str] = None, force_reapprove: bool = False, device_name: Optional[str] = None, prompt: Optional[str] = None) -> str:
        params = {
            "client_id": self.app_key,
            "redirect_uri": self.redirect_uri,
            "response_type": "code",
        }
        if state:
            params["state"] = state
        if force_reapprove:
            params["force_reapprove"] = 1
        if device_name:
            params["device_name"] = device_name
        if prompt:
            params["prompt"] = prompt

        auth_base = (self.http.base_url.replace("api.", "u.").replace("eapi.", "eu."))
        return f"{auth_base}/oauth2/authorize?{urlencode(params)}"

    def finish(self, code: str) -> OAuthToken:
        data = self.http.request(
            "oauth2_token",
            {
                "client_id": self.app_key,
                "client_secret": self.app_secret,
                "code": code,
                "grant_type": "authorization_code",
                "redirect_uri": self.redirect_uri,
            },
            http_method="POST",
        )
        token = data.get("access_token")
        if not token:
            raise RuntimeError("No access_token in OAuth response")
        return OAuthToken(access_token=token)

class PCloudOAuth2FlowNoRedirect(PCloudOAuth2Flow):
    """CLI flow; call start() then paste code to finish()."""
    pass
