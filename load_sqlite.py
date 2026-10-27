
import csv
import sqlite3
from pathlib import Path

ROOT = Path(".")
DB_DIR = ROOT / "database"
DB_DIR.mkdir(exist_ok=True)

DB_PATH = DB_DIR / "loan_decision_engine.db"
SCHEMA_PATH = ROOT / "sql" / "schema.sql"

TABLE_CONFIG = [
    ("master", "applicants.csv", "Applicant"),
    ("master", "employment.csv", "Employment"),
    ("master", "income_records.csv", "IncomeRecord"),
    ("master", "credit_facilities.csv", "CreditFacility"),
    ("master", "loan_products.csv", "LoanProduct"),
    ("transactions", "loan_applications.csv", "LoanApplication"),
    ("transactions", "affordability_checks.csv", "AffordabilityCheck"),
    ("transactions", "decisions.csv", "Decision"),
    ("transactions", "repayment_schedules.csv", "RepaymentSchedule"),
    ("transactions", "documents.csv", "Document"),
    ("transactions", "event_history.csv", "EventHistory"),
]

def load_csv(path):
    with path.open("r", newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        return reader.fieldnames, list(reader)


def main():
    if not SCHEMA_PATH.exists():
        raise FileNotFoundError(f"Schema not found: {SCHEMA_PATH}")

    if DB_PATH.exists():
        DB_PATH.unlink()

    connection = sqlite3.connect(DB_PATH)

    try:
        connection.execute("PRAGMA foreign_keys = ON")

        schema = SCHEMA_PATH.read_text(encoding="utf-8")
        connection.executescript(schema)

        for folder, filename, table in TABLE_CONFIG:
            csv_path = ROOT / "data" / folder / filename

            if not csv_path.exists():
                raise FileNotFoundError(f"CSV not found: {csv_path}")

            columns, rows = load_csv(csv_path)

            if not columns:
                raise ValueError(f"No columns found in {csv_path}")

            column_sql = ", ".join(f'"{column}"' for column in columns)
            placeholders = ", ".join("?" for _ in columns)

            insert_sql = (
                f'INSERT INTO "{table}" ({column_sql}) '
                f"VALUES ({placeholders})"
            )

            values = [
                tuple(row[column] for column in columns)
                for row in rows
            ]

            connection.executemany(insert_sql, values)
            print(f"Loaded {table}: {len(rows)} rows")

        connection.commit()

        violations = connection.execute(
            "PRAGMA foreign_key_check"
        ).fetchall()

        if violations:
            raise ValueError(
                f"Foreign key violations found: {violations[:10]}"
            )

        print("PASS: Foreign key integrity check")

    finally:
        connection.close()

    print(f"SQLite database created: {DB_PATH}")


if __name__ == "__main__":
    main()
