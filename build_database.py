import sqlite3
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
DATABASE_DIR = BASE_DIR / "database"
DATABASE_PATH = DATABASE_DIR / "university.db"
SCHEMA_PATH = DATABASE_DIR / "schema.sql"
SEED_DATA_PATH = DATABASE_DIR / "seed_data.sql"


def run_sql_file(connection: sqlite3.Connection, sql_path: Path) -> None:
    """Execute all SQL statements from a file."""
    with open(sql_path, "r", encoding="utf-8") as file:
        sql_script = file.read()
    connection.executescript(sql_script)


def build_database() -> None:
    """Create and populate the SQLite database."""
    DATABASE_DIR.mkdir(exist_ok=True)

    with sqlite3.connect(DATABASE_PATH) as connection:
        connection.execute("PRAGMA foreign_keys = ON;")
        run_sql_file(connection, SCHEMA_PATH)
        run_sql_file(connection, SEED_DATA_PATH)
        connection.commit()

    print(f"Database created successfully at: {DATABASE_PATH}")


if __name__ == "__main__":
    build_database()