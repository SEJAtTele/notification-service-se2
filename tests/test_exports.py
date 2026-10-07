"""
Existing tests. They pass. Whether they test the right things is a different
question.
"""

import pytest

from app import email_provider, exports


@pytest.fixture(autouse=True)
def reset_state():
    email_provider.provider = email_provider.FakeEmailProvider()
    exports.store = exports.ExportStore()
    yield


def test_complete_export_marks_complete():
    exports.store.create("exp_1", "ada@example.com")
    result = exports.complete_export("exp_1", "exp_1.zip")
    assert result["status"] == "complete"
    assert exports.store.get("exp_1").status == "complete"


def test_complete_export_sends_email():
    exports.store.create("exp_1", "ada@example.com")
    exports.complete_export("exp_1", "exp_1.zip")
    sent = email_provider.provider.emails_to("ada@example.com")
    assert len(sent) >= 1
    assert "exp_1.zip" in sent[0].body


def test_complete_export_survives_transient_failure():
    exports.store.create("exp_1", "ada@example.com")
    email_provider.provider.fail_next = 1
    exports.complete_export("exp_1", "exp_1.zip")
    assert len(email_provider.provider.emails_to("ada@example.com")) == 1
