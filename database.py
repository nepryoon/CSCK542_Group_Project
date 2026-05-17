import sqlite3
from pathlib import Path

import pandas as pd


BASE_DIR = Path(__file__).resolve().parent
DATABASE_PATH = BASE_DIR / "database" / "university.db"


def get_connection() -> sqlite3.Connection:
    """Return a new connection to the university SQLite database."""
    connection = sqlite3.connect(DATABASE_PATH)
    # sqlite3.Row enables column-name access (row["name"]) instead of
    # positional indexing, which breaks silently when column order changes.
    connection.row_factory = sqlite3.Row
    return connection


def run_query(query: str, params: tuple = ()) -> pd.DataFrame:
    """Run a parameterised SQL query and return the result as a DataFrame."""
    # The context manager closes the connection even if pd.read_sql_query
    # raises, preventing file-handle leaks under concurrent requests.
    with get_connection() as connection:
        return pd.read_sql_query(query, connection, params=params)


def build_where(conditions: list[str], params: list) -> tuple[str, tuple]:
    """Turn a list of SQL condition strings into a WHERE clause and params tuple.

    Keeps callers from building WHERE strings by hand, which risks
    forgetting the keyword or misplacing AND operators.

    Example:
        clause, params = build_where(["name = ?"], ["Alice"])
        # clause == "WHERE name = ?"
        # params == ("Alice",)
    """
    clause = ("WHERE " + " AND ".join(conditions)) if conditions else ""
    return clause, tuple(params)
