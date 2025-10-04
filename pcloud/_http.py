from __future__ import annotations
from typing import Any, Dict, Optional, Tuple
import requests
from .errors import PCloudError, PCloudHTTPError

US_API = "https://api.pcloud.com"
EU_API = "https://eapi.pcloud.com"

DEFAULT_TIMEOUT: Tuple[float, float] = (10.0, 120.0)

class HTTP:
    def __init__(self, *, base_url: str, token: Optional[str] = None, timeout: Tuple[float, float] = DEFAULT_TIMEOUT, session: Optional[requests.Session] = None) -> None:
        self.base_url = base_url
        self.token = token
        self.timeout = timeout
        self.session = session or requests.Session()

    def set_token(self, token: Optional[str]) -> None:
        self.token = token

    def request(
        self,
        method: str,
        params: Optional[Dict[str, Any]] = None,
        *,
        files: Optional[Dict[str, Any]] = None,
        http_method: str = "GET",
        stream: bool = False,
    ) -> Any:
        url = f"{self.base_url}/{method}"
        headers = {"Authorization": f"Bearer {self.token}"} if self.token else {}

        try:
            if http_method.upper() == "GET" and not files:
                resp = self.session.get(url, params=params, headers=headers, timeout=self.timeout, stream=stream)
            else:
                resp = self.session.post(url, data=params, files=files, headers=headers, timeout=self.timeout, stream=stream)
        except requests.RequestException as e:  # pragma: no cover - network
            raise PCloudHTTPError(f"Network error: {e}")

        if stream:
            resp.raise_for_status()
            return resp

        try:
            resp.raise_for_status()
            data = resp.json()
        except requests.HTTPError as e:
            raise PCloudHTTPError(f"HTTP error: {e}", status=getattr(resp, "status_code", None))
        except ValueError as e:
            raise PCloudHTTPError(f"Invalid JSON: {e}")

        if isinstance(data, dict) and data.get("result", 0) != 0:
            raise PCloudError(result=int(data.get("result", -1)), error=str(data.get("error", "Unknown error")), data=data)
        return data
