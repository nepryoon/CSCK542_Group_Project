"""
Shared pytest fixtures for the university record management system tests.

All tests that need a database receive an isolated in-memory SQLite instance
built from the real schema and seed files so the production DB is never touched.
"""

import sqlite3
import sys
import tempfile
import shutil
from pathlib import Path
from unittest.mock import patch

import pandas as pd
import pytest
from fastapi.testclient import TestClient

# Make the project root importable regardless of where pytest is invoked from.
ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

SCHEMA_PATH = ROOT / "database" / "schema.sql"
SEED_PATH = ROOT / "database" / "seed_data.sql"


def _load_sql(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _build_db(conn: sqlite3.Connection) -> None:
    conn.execute("PRAGMA foreign_keys = ON;")
    conn.executescript(_load_sql(SCHEMA_PATH))
    conn.executescript(_load_sql(SEED_PATH))
    conn.commit()


@pytest.fixture(scope="session")
def in_memory_db() -> sqlite3.Connection:
    """
    Session-scoped in-memory SQLite DB loaded with schema + seed data.
    Safe for read-only tests only - writes persist for the whole session.
    check_same_thread=False so the connection can be used in the query
    unit tests which call pd.read_sql_query directly.
    """
    conn = sqlite3.connect(":memory:", check_same_thread=False)
    conn.row_factory = sqlite3.Row
    _build_db(conn)
    yield conn
    conn.close()


@pytest.fixture()
def isolated_db() -> sqlite3.Connection:
    """
    Function-scoped in-memory database - use for tests that write data
    so they cannot pollute each other.
    """
    conn = sqlite3.connect(":memory:", check_same_thread=False)
    conn.row_factory = sqlite3.Row
    _build_db(conn)
    yield conn
    conn.close()


def _make_run_query(conn: sqlite3.Connection):
    """
    Return a run_query shim bound to *conn*.
    check_same_thread=False on the connection means this is safe to call
    from FastAPI's worker thread pool.
    """
    def run_query(query: str, params: tuple = ()) -> pd.DataFrame:
        return pd.read_sql_query(query, conn, params=params)
    return run_query


@pytest.fixture()
def db_run_query(in_memory_db):
    """A run_query callable bound to the session-scoped in-memory DB."""
    return _make_run_query(in_memory_db)


@pytest.fixture()
def api_client(in_memory_db):
    """
    FastAPI TestClient with run_query patched in every module that imports it.
    The patch targets the name as it exists in each module's namespace so
    FastAPI's worker threads call our shim rather than the real function.
    """
    rq = _make_run_query(in_memory_db)

    with patch("database.run_query", side_effect=rq), \
         patch("queries.run_query", side_effect=rq), \
         patch("main.run_query", side_effect=rq):
        from main import app
        client = TestClient(app)
        yield client
