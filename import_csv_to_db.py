import csv
import sqlite3
from pathlib import Path

DB_PATH = Path("lotto-539.db")
CSV_FILES = ["今彩539_2022.csv", "今彩539_2023.csv"]


def parse_and_insert(csv_path, db_path):
    with open(csv_path, encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        rows = []
        for row in reader:
            nums = sorted([row["獎號1"], row["獎號2"], row["獎號3"], row["獎號4"], row["獎號5"]])
            rows.append({
                "期別": row["期別"],
                "開獎日": row["開獎日期"],
                "大小順序": " ".join(nums),
                "頭獎中獎注數": 0,
            })

    before = conn.total_changes
    conn.executemany(
        """INSERT OR IGNORE INTO history (期別, 開獎日, 大小順序, 頭獎中獎注數)
           VALUES (:期別, :開獎日, :大小順序, :頭獎中獎注數)""",
        rows,
    )
    return conn.total_changes - before


conn = sqlite3.connect(str(DB_PATH))
total_inserted = 0
for csv_file in CSV_FILES:
    n = parse_and_insert(csv_file, DB_PATH)
    total_inserted += n
    print(f"{csv_file}: 讀取完成，新增 {n} 筆")

conn.commit()
conn.close()
print(f"全部完成，共新增 {total_inserted} 筆")
