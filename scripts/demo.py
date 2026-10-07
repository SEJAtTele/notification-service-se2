"""
Reproduces the two production problems locally.

    python scripts/demo.py

Expected output before any changes: the slow call takes ~2s, and the retry
scenario sends the user two emails.
"""

import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app import email_provider, exports  # noqa: E402


def problem_1_slow_provider():
    print("--- Problem 1: slow provider blocks the request ---")
    email_provider.provider = email_provider.FakeEmailProvider(latency_seconds=2.0)
    exports.store = exports.ExportStore()
    exports.store.create("exp_slow", "ada@example.com")

    t0 = time.perf_counter()
    exports.complete_export("exp_slow", "exp_slow.zip")
    elapsed = time.perf_counter() - t0
    print(f"complete_export() took {elapsed:.2f}s  (target: well under 0.1s)\n")


def problem_2_retry_duplicates():
    print("--- Problem 2: caller retry sends duplicate email ---")
    email_provider.provider = email_provider.FakeEmailProvider()
    exports.store = exports.ExportStore()
    exports.store.create("exp_dup", "ada@example.com")

    # Simulate the export worker retrying because it didn't get a response
    # in time (network timeout, worker restart, user mashing the button...).
    exports.complete_export("exp_dup", "exp_dup.zip")
    exports.complete_export("exp_dup", "exp_dup.zip")

    n = len(email_provider.provider.emails_to("ada@example.com"))
    print(f"emails sent to user: {n}  (target: 1)\n")


def problem_3_provider_down():
    print("--- Problem 3: provider outage loses the email ---")
    email_provider.provider = email_provider.FakeEmailProvider(down=True)
    exports.store = exports.ExportStore()
    exports.store.create("exp_down", "ada@example.com")

    exports.complete_export("exp_down", "exp_down.zip")
    email_provider.provider.down = False  # provider recovers
    time.sleep(0.5)  # give any background machinery a chance

    n = len(email_provider.provider.emails_to("ada@example.com"))
    print(f"emails sent after recovery: {n}  (target: 1)\n")


if __name__ == "__main__":
    import logging

    logging.basicConfig(level=logging.WARNING, format="%(levelname)s %(message)s")
    problem_1_slow_provider()
    problem_2_retry_duplicates()
    problem_3_provider_down()
