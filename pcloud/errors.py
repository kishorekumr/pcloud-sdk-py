from __future__ import annotations
from dataclasses import dataclass
from typing import Optional, Dict, Any

@dataclass
class PCloudError(Exception):
    """Logical API error (`result != 0`) returned by pCloud."""
    result: int
    error: str
    data: Optional[Dict[str, Any]] = None

    def __str__(self) -> str:  # pragma: no cover - trivial
        return f"pCloud API Error {self.result}: {self.error}"

class PCloudHTTPError(Exception):
    """HTTP or JSON parsing error before API-level `result` is known."""
    def __init__(self, message: str, *, status: Optional[int] = None) -> None:
        super().__init__(message)
        self.status = status
