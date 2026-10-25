"""SQLite loading and SQL query execution."""

from pathlib import Path
import sqlite3
import pandas as pd


def load_to_sqlite(df: pd.DataFrame, database_path: Path) -> None:
    """Load cleaned appointments into a local SQLite database."""
    database_path.parent.mkdir(parents=True, exist_ok=True)
    sql_df = df.copy()
    sql_df["appointment_date"] = pd.to_datetime(sql_df["appointment_date"]).dt.strftime("%Y-%m-%d")
    with sqlite3.connect(database_path) as conn:
        sql_df.to_sql("appointments", conn, if_exists="replace", index=False)
        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_appointments_date "
            "ON appointments(appointment_date)"
        )
        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_appointments_department "
            "ON appointments(department)"
        )


def run_sql_query(database_path: Path, query: str) -> pd.DataFrame:
    """Execute a read-only-style analytical query and return its result."""
    with sqlite3.connect(database_path) as conn:
        return pd.read_sql_query(query, conn)
