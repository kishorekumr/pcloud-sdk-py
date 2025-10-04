from __future__ import annotations
import os
from typing import Any, Callable, Dict, Optional
from ._http import HTTP

class Files:
    def __init__(self, http: HTTP) -> None:
        self._http = http

    def list_folder(self, *, folderid: Optional[int] = None, path: Optional[str] = None, recursive: bool = False) -> Dict[str, Any]:
        if not folderid and not path:
            raise ValueError("Provide folderid or path")
        params: Dict[str, Any] = {"recursive": 1 if recursive else 0}
        if folderid is not None:
            params["folderid"] = int(folderid)
        if path is not None:
            params["path"] = path
        return self._http.request("listfolder", params)

    def create_folder(self, *, path: Optional[str] = None, folderid: Optional[int] = None, name: Optional[str] = None) -> Dict[str, Any]:
        if path:
            return self._http.request("mkdir", {"path": path})
        if folderid is not None and name:
            return self._http.request("createfolder", {"folderid": int(folderid), "name": name})
        raise ValueError("Provide path or (folderid & name)")

    def delete_file(self, *, fileid: Optional[int] = None, path: Optional[str] = None) -> Dict[str, Any]:
        if fileid is not None:
            return self._http.request("deletefile", {"fileid": int(fileid)})
        if path is not None:
            return self._http.request("deletefile", {"path": path})
        raise ValueError("Provide fileid or path")

    def files_upload(self, local_path: str, *, folderid: Optional[int] = None, path: Optional[str] = None, rename_if_exists: bool = True, on_progress: Optional[Callable[[int, int], None]] = None) -> Dict[str, Any]:
        if not os.path.isfile(local_path):
            raise FileNotFoundError(local_path)
        params: Dict[str, Any] = {"nopartial": 1, "renameifexists": 1 if rename_if_exists else 0}
        if folderid is not None:
            params["folderid"] = int(folderid)
        elif path is not None:
            params["path"] = path
        else:
            raise ValueError("Provide destination folderid or path")

        size = os.path.getsize(local_path)

        class _Reader:
            def __init__(self, fp, total):
                self.fp = fp
                self.total = total
                self.read_so_far = 0
            def read(self, amt: int = -1):
                chunk = self.fp.read(amt)
                if chunk and on_progress:
                    self.read_so_far += len(chunk)
                    on_progress(self.read_so_far, self.total)
                return chunk
            def __getattr__(self, name):
                return getattr(self.fp, name)

        with open(local_path, "rb") as raw:
            wrapped = _Reader(raw, size)
            files = {"file": (os.path.basename(local_path), wrapped)}
            return self._http.request("uploadfile", params, files=files, http_method="POST")

    def files_download(self, *, fileid: Optional[int] = None, path: Optional[str] = None, dest_path: str, on_progress: Optional[Callable[[int, Optional[int]], None]] = None, chunk_size: int = 1024 * 1024) -> str:
        link = self.get_file_link(fileid=fileid, path=path)
        resp = self._http.session.get(link, stream=True, timeout=self._http.timeout)
        resp.raise_for_status()
        total = int(resp.headers.get("Content-Length", 0)) or None
        os.makedirs(os.path.dirname(os.path.abspath(dest_path)) or ".", exist_ok=True)
        downloaded = 0
        with open(dest_path, "wb") as f:
            for chunk in resp.iter_content(chunk_size=chunk_size):
                if not chunk:
                    continue
                f.write(chunk)
                downloaded += len(chunk)
                if on_progress:
                    on_progress(downloaded, total)
        return dest_path

    def get_file_link(self, *, fileid: Optional[int] = None, path: Optional[str] = None) -> str:
        params: Dict[str, Any] = {}
        if fileid is not None:
            params["fileid"] = int(fileid)
        elif path is not None:
            params["path"] = path
        else:
            raise ValueError("Provide fileid or path")
        data = self._http.request("getfilelink", params)
        hosts = data.get("hosts") or []
        file_path = data.get("path")
        if not hosts or not file_path:
            raise RuntimeError("Malformed getfilelink response")
        return f"https://{hosts[0]}{file_path}"
