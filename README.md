# pcloud-python-sdk

[![PyPI version](https://img.shields.io/pypi/v/pcloud-python-sdk.svg)](https://pypi.org/project/pcloud-python-sdk/)
![CI](https://github.com/you/pcloud-python-sdk/actions/workflows/ci.yml/badge.svg)

Dropbox-style Python SDK for the pCloud API.

## Install
```bash
pip install pcloud-python-sdk
```

## Quickstart
```python
from pcloud import PCloud, PCloudOAuth2Flow

# 1) OAuth flow (web) — paste the code back
flow = PCloudOAuth2Flow(app_key, app_secret, redirect_uri, location="EU")
print("Go to:", flow.start(state="xyz"))
code = input("Paste code: ").strip()
token = flow.finish(code)

# 2) Use the client
pc = PCloud(access_token=token.access_token)
print(pc.files.list_folder(folderid=0))
```

## Upload with progress
```python
from pcloud import PCloud
pc = PCloud(access_token="...")

def on_progress(done, total):
    if total:
        pct = 100.0 * done / total
        print(f"Uploaded {done}/{total} bytes ({pct:.1f}%)")
    else:
        print(f"Uploaded {done} bytes")

pc.files.files_upload("local.jpg", folderid=0, on_progress=on_progress)
```

## Download with progress
```python
from pcloud import PCloud
pc = PCloud(access_token="...")

def on_progress(done, total):
    if total:
        pct = 100.0 * done / total
        print(f"Downloaded {done}/{total} bytes ({pct:.1f}%)")
    else:
        print(f"Downloaded {done} bytes")

pc.files.files_download(fileid=12345, dest_path="./local.jpg", on_progress=on_progress)
```

## API surface
- `pcloud.PCloud`: top-level client
- `pcloud.PCloudOAuth2Flow` / `pcloud.PCloudOAuth2FlowNoRedirect`: OAuth helpers
- `client.files.*`:
  - `list_folder`, `create_folder`, `delete_file`
  - `files_upload`, `files_download`, `get_file_link`

This mirrors the ergonomics of the Dropbox Python SDK while using pCloud endpoints under the hood.

## Development
```bash
python -m pip install -U pip
pip install -e .
pip install pytest ruff mypy
pytest -q
```

## Releasing
- Create a PyPI project & token.
- Locally:
  ```bash
  python -m pip install -U build twine
  python -m build
  twine check dist/*
  twine upload dist/*
  ```
- Or tag `vX.Y.Z` and let GitHub Actions publish (see `.github/workflows/release.yml`).

## License
MIT
