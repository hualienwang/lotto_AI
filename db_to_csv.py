#!/usr/bin/env python3
import csv
import sqlite3
from pathlib import Path


def export_sqlite_to_csv(db_path: Path, csv_path: Path, table_name: str = 'history') -> None:
    db_path = db_path.resolve()
    csv_path = csv_path.resolve()

    if not db_path.exists():
        raise FileNotFoundError(f'Database not found: {db_path}')

    with sqlite3.connect(str(db_path)) as conn:
        cursor = conn.cursor()
        cursor.execute(f'SELECT * FROM "{table_name}" ORDER BY "期別" DESC')
        rows = cursor.fetchall()
        if not rows:
            raise ValueError(f'No rows found in table: {table_name}')

        headers = [description[0] for description in cursor.description]
        size_order_index = headers.index('大小順序') if '大小順序' in headers else None

        csv_path.parent.mkdir(parents=True, exist_ok=True)
        with open(csv_path, 'w', encoding='utf-8-sig', newline='') as csv_file:
            writer = csv.writer(csv_file)
            writer.writerow(headers)
            for row in rows:
                row = list(row)
                if size_order_index is not None and row[size_order_index] is not None:
                    row[size_order_index] = row[size_order_index].replace(' ', ',')
                writer.writerow(row)

    print(f'Exported {len(rows)} rows from {db_path.name} to {csv_path.name}')


if __name__ == '__main__':
    base = Path(__file__).parent
    default_db = base / 'lotto-539.db'
    default_csv = base / 'lotto-539.csv'
    export_sqlite_to_csv(default_db, default_csv)
