import sqlite3
from pathlib import Path

import pandas as pd


BASE_DIR = Path(__file__).resolve().parent
DATABASE_PATH = BASE_DIR / "database" / "university.db"


def get_connection() -> sqlite3.Connection:
    """Create a connection to the SQLite database."""
    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def run_query(query: str, params: tuple = ()) -> pd.DataFrame:
    """Run a SQL query and return the result as a pandas DataFrame."""
    with get_connection() as connection:
        return pd.read_sql_query(query, connection, params=params)
    