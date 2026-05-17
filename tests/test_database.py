"""
Unit tests for database.py - get_connection and run_query.
"""

import sqlite3
from pathlib import Path
from unittest.mock import MagicMock, patch

import pandas as pd
import pytest

import database


class TestGetConnection:
    def test_returns_sqlite_connection(self):
        conn = database.get_connection()
        assert isinstance(conn, sqlite3.Connection)
        conn.close()

    def test_row_factory_is_set(self):
        conn = database.get_connection()
        assert conn.row_factory == sqlite3.Row
        conn.close()

    def test_connects_to_correct_path(self):
        conn = database.get_connection()
        # SQLite exposes the db path via a pragma
        cursor = conn.execute("PRAGMA database_list")
        row = cursor.fetchone()
        actual_path = Path(row[2]).resolve()
        expected_path = database.DATABASE_PATH.resolve()
        assert actual_path == expected_path
        conn.close()

    def test_connection_is_usable(self):
        conn = database.get_connection()
        result = conn.execute("SELECT 1 AS val").fetchone()
        assert result["val"] == 1
        conn.close()


class TestRunQuery:
    def test_returns_dataframe(self, in_memory_db):
        with patch("database.get_connection", return_value=in_memory_db):
            result = database.run_query("SELECT 1 AS n")
        assert isinstance(result, pd.DataFrame)

    def test_simple_select(self, in_memory_db):
        with patch("database.get_connection", return_value=in_memory_db):
            df = database.run_query("SELECT COUNT(*) AS c FROM departments")
        assert df.iloc[0]["c"] == 4

    def test_parameterised_query(self, in_memory_db):
        with patch("database.get_connection", return_value=in_memory_db):
            df = database.run_query(
                "SELECT department_name FROM departments WHERE department_id = ?",
                ("D001",),
            )
        assert df.iloc[0]["department_name"] == "Computer Science"

    def test_empty_result_is_empty_dataframe(self, in_memory_db):
        with patch("database.get_connection", return_value=in_memory_db):
            df = database.run_query(
                "SELECT * FROM departments WHERE department_id = ?",
                ("NONEXISTENT",),
            )
        assert isinstance(df, pd.DataFrame)
        assert len(df) == 0

    def test_columns_match_query(self, in_memory_db):
        with patch("database.get_connection", return_value=in_memory_db):
            df = database.run_query(
                "SELECT department_id, department_name FROM departments LIMIT 1"
            )
        assert list(df.columns) == ["department_id", "department_name"]

    def test_multiple_rows_returned(self, in_memory_db):
        with patch("database.get_connection", return_value=in_memory_db):
            df = database.run_query("SELECT * FROM lecturers")
        assert len(df) == 5

    def test_default_params_is_empty_tuple(self, in_memory_db):
        """run_query must work with no params argument."""
        with patch("database.get_connection", return_value=in_memory_db):
            df = database.run_query("SELECT 42 AS answer")
        assert df.iloc[0]["answer"] == 42

    def test_invalid_sql_raises(self, in_memory_db):
        with patch("database.get_connection", return_value=in_memory_db):
            with pytest.raises(Exception):
                database.run_query("THIS IS NOT SQL")
