from __future__ import annotations
from typing import Optional, Tuple
import requests
from ._http import HTTP, EU_API, US_API
from .files import Files

class PCloud:
    """Top-level client, similar to `dropbox.Dropbox`.

    Examples
    --------
    from pcloud import PCloud
    pc = PCloud(access_token="...", location="EU")
    pc.files.list_folder(folderid=0)
    pc.files.files_upload("local.jpg", folderid=0)
    """
    def __init__(self, *, access_token: Optional[str] = None, location: str = "EU", timeout: Tuple[float, float] = (10, 120), session: Optional[requests.Session] = None) -> None:
        base = EU_API if location.upper() == "EU" else US_API
        self._http = HTTP(base_url=base, token=access_token, timeout=timeout, session=session)
        self.files = Files(self._http)
    def set_access_token(self, token: Optional[str]) -> None:
        self._http.set_token(token)
