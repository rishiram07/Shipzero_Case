"""Task 1 - runs the SQL file with DuckDB and saves the results."""

import os
from pathlib import Path

import duckdb

ROOT = Path(__file__).resolve().parent.parent
SQL_FILE = ROOT / "sql" / "task1_activity_monitoring.sql"
OUTPUT_DIR = ROOT / "output"

TITLES = [
    "Task 1a - active / inactive vehicles",
    "Task 1b - vehicle with the most tracking points",
]
OUTPUT_FILES = ["task1a_active_vehicles.csv", "task1b_top_vehicle.csv"]


def main():
    os.chdir(ROOT)  # so 'data/...' paths in the SQL work
    OUTPUT_DIR.mkdir(exist_ok=True)

    con = duckdb.connect()  # in-memory database
    statements = con.extract_statements(SQL_FILE.read_text(encoding="utf-8"))

    query_no = 0
    for stmt in statements:
        # CREATE VIEW statements: just run them
        if stmt.type != duckdb.StatementType.SELECT:
            con.execute(stmt)
            continue

        # SELECT statements: print and save the result
        df = con.execute(stmt).df()
        print(f"\n=== {TITLES[query_no]} ===")
        print(df.to_string(index=False))
        df.to_csv(OUTPUT_DIR / OUTPUT_FILES[query_no], index=False)
        query_no += 1

    print("\nSaved results to output/")


if __name__ == "__main__":
    main()