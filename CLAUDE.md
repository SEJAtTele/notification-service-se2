# Project notes for coding agents

- Python 3.11+, standard library + pytest only. Do not add dependencies
  without the human confirming.
- Run `pytest` from the repo root. Tests must stay deterministic: no
  `time.sleep` in tests.
- `app/email_provider.py` is a stand-in for a third-party API. Do not modify
  its behaviour; change how it is called.
- Do not modify or delete existing tests without saying so explicitly.
