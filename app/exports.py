"""
Export completion handling.

This is the code the exercise asks you to change. It represents the request
handler that runs when an export job finishes (in the real app this is an HTTP
endpoint hit by the export worker; here it's a plain function).
"""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field

from app import email_provider
from app.email_provider import ProviderUnavailable

log = logging.getLogger(__name__)

DOWNLOAD_BASE_URL = "https://app.example.com/downloads"


@dataclass
class Export:
    export_id: str
    user_email: str
    status: str = "pending"  # pending | complete
    download_path: str | None = None
    completed_at: float | None = None


@dataclass
class ExportStore:
    """In-memory stand-in for the exports table."""

    _rows: dict[str, Export] = field(default_factory=dict)

    def create(self, export_id: str, user_email: str) -> Export:
        row = Export(export_id=export_id, user_email=user_email)
        self._rows[export_id] = row
        return row

    def get(self, export_id: str) -> Export:
        return self._rows[export_id]


store = ExportStore()


def complete_export(export_id: str, download_path: str) -> dict:
    """
    Called when an export job finishes. Marks the export complete and emails
    the user a download link.

    Returns a response body. The caller (export worker) treats anything other
    than a clean return as failure and will retry the whole call.
    """
    export = store.get(export_id)

    export.status = "complete"
    export.download_path = download_path
    export.completed_at = time.time()

    link = f"{DOWNLOAD_BASE_URL}/{download_path}"
    subject = "Your export is ready"
    body = f"Your export is ready. Download it here: {link}"

    # Retry a few times so a blip at the provider doesn't fail the request.
    for attempt in range(3):
        try:
            email_provider.provider.send(export.user_email, subject, body)
            break
        except ProviderUnavailable as e:
            log.warning("email send failed (attempt %d): %s", attempt + 1, e)
            time.sleep(0.1)
    else:
        log.error("giving up on email for export %s", export_id)

    return {"export_id": export_id, "status": export.status, "link": link}
