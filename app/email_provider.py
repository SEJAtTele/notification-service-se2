"""
Fake third-party email provider.

Stands in for SendGrid / SES / Postmark. Simulates latency and outages so the
exercise can be run with no network. Candidates may read this file but should
treat it as an external dependency: assume you cannot change the provider's
behaviour, only how you call it.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field


class ProviderUnavailable(Exception):
    """Raised when the provider is 'down' (think HTTP 503)."""


@dataclass
class SentEmail:
    provider_message_id: str
    to: str
    subject: str
    body: str
    sent_at: float


@dataclass
class FakeEmailProvider:
    """
    Configurable fake.

    latency_seconds: how long each send() takes.
    fail_next:       number of upcoming send() calls that will raise
                     ProviderUnavailable. Decrements on each failure.
    down:            if True, every send() raises until set back to False.
    """

    latency_seconds: float = 0.0
    fail_next: int = 0
    down: bool = False
    outbox: list[SentEmail] = field(default_factory=list)
    call_count: int = 0

    def send(self, to: str, subject: str, body: str) -> str:
        """
        Send an email. Returns the provider's message id.

        Like a real provider, this has no idempotency of its own: call it
        twice with the same arguments and two emails go out.
        """
        self.call_count += 1
        time.sleep(self.latency_seconds)

        if self.down:
            raise ProviderUnavailable("provider is down")
        if self.fail_next > 0:
            self.fail_next -= 1
            raise ProviderUnavailable("transient provider error")

        msg = SentEmail(
            provider_message_id=f"msg_{uuid.uuid4().hex[:12]}",
            to=to,
            subject=subject,
            body=body,
            sent_at=time.time(),
        )
        self.outbox.append(msg)
        return msg.provider_message_id

    def emails_to(self, address: str) -> list[SentEmail]:
        return [m for m in self.outbox if m.to == address]


# Module-level singleton, the way the real client is wired up today.
provider = FakeEmailProvider()
