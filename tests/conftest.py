"""Shared pytest setup.

Dummy env vars are set BEFORE any `app.*` module is imported anywhere in
the test session, so app.config's required-secret checks pass without
needing real credentials for the default (non-live) test run. Tests
marked @pytest.mark.live are skipped by default (see pytest.ini) - run
them explicitly with real credentials exported first: e.g.
    GEMINI_API_KEY=<real key> pytest -m live
"""

import os
import tempfile
from pathlib import Path

# A session-wide throwaway directory - set as the DEFAULT DB_PATH before
# app.config is ever imported, so even the module-level storage.init_db()
# call in app/main.py (triggered by the first `import app.main` anywhere
# in the session, e.g. from test_webhook.py) never touches the real
# data/app.db. Per-test isolation on top of this comes from the temp_db
# fixture below, which monkeypatches config.DB_PATH further.
_SESSION_TEST_DATA_DIR = Path(tempfile.mkdtemp(prefix="novatech_test_"))

os.environ.setdefault("PAGE_ACCESS_TOKEN", "test-page-access-token")
os.environ.setdefault("GEMINI_API_KEY", "test-gemini-key")
os.environ.setdefault("GROQ_API_KEY", "test-groq-key")
os.environ.setdefault("APP_SECRET", "test-app-secret")
os.environ.setdefault("DB_PATH", str(_SESSION_TEST_DATA_DIR / "app.db"))

import pytest

from app import config, storage


@pytest.fixture
def temp_db(tmp_path, monkeypatch):
    """An isolated SQLite file for one test. app.storage reads
    config.DB_PATH at call time (see app/storage.py's _connect()), so
    monkeypatching the attribute here is enough - no need to reload or
    patch already-imported modules."""

    db_path = tmp_path / "test.db"
    monkeypatch.setattr(config, "DB_PATH", db_path)
    storage.init_db()

    return db_path
