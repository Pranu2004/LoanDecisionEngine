
import sqlite3
from pathlib import Path

db_path = Path("database/loan_decision_engine.db")

if not db_path.exists():
    print("ERROR: Database file not found. Run python load_sqlite.py first.")
else:
    connection = sqlite3.connect(db_path)

    print("DATABASE TABLES AND ROW COUNTS")
    print("-" * 40)

    query = """
        SELECT name
        FROM sqlite_master
        WHERE type = 'table'
          AND name NOT LIKE 'sqlite_%'
        ORDER BY name
    """

    tables = connection.execute(query).fetchall()

    for (table_name,) in tables:
        count = connection.execute(
            f'SELECT COUNT(*) FROM "{table_name}"'
        ).fetchone()[0]
        print(f"{table_name}: {count} rows")

    connection.close()
