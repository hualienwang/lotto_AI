#!/usr/bin/env python3
import sqlite3
import csv
from pathlib import Path

def parse_numbers(numbers_text):
    """Parse a string of numbers into a list of integers."""
    import re
    numbers = []
    for value in re.split(r'[\s,，]+', str(numbers_text).strip()):
        if not value:
            continue
        try:
            number = int(value.strip())
        except ValueError:
            continue
        if 1 <= number <= 39 and number not in numbers:
            numbers.append(number)
    return numbers

def import_csv_to_db(csv_path, db_path):
    """Import CSV file data to SQLite database."""
    print(f"Importing {csv_path} to {db_path}...")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Ensure table exists
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS history (
            "期別" TEXT PRIMARY KEY,
            "開獎日" TEXT NOT NULL,
            "大小順序" TEXT NOT NULL,
            "頭獎中獎注數" INTEGER NOT NULL
        )
    """)
    
    imported = 0
    updated = 0
    
    with open(csv_path, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                # Extract data
                period = row['期別'].strip()
                draw_date = row['開獎日期'].strip()
                
                # Parse award numbers (獎號1 to 獎號5)
                numbers = []
                for i in range(1, 6):
                    col_name = f'獎號{i}'
                    if col_name in row and row[col_name].strip():
                        numbers.extend(parse_numbers(row[col_name]))
                
                # Sort numbers and create sorted string
                numbers = sorted(set(numbers))
                sorted_numbers = ','.join(f'{n:02d}' for n in numbers)
                
                # Get 頭獎中獎注數 (default to 0 if not available)
                head_prize_count = 0
                try:
                    head_prize_count = int(row.get('頭獎中獎注數', 0) or 0)
                except (ValueError, TypeError):
                    head_prize_count = 0
                
                # Try to insert, if exists then update
                cursor.execute(
                    """INSERT OR REPLACE INTO history 
                       ("期別", "開獎日", "大小順序", "頭獎中獎注數") 
                       VALUES (?, ?, ?, ?)""",
                    (period, draw_date, sorted_numbers, head_prize_count)
                )
                
                # Check if this was an insert or update
                cursor.execute("SELECT changes()")
                if cursor.fetchone()[0] > 0:
                    imported += 1
                else:
                    updated += 1
                    
                print(f"  期別: {period}, 日期: {draw_date}, 號碼: {sorted_numbers}")
                    
            except Exception as e:
                print(f"  ERROR processing row: {row}")
                print(f"  {e}")
    
    conn.commit()
    
    # Show final sorted data
    print(f"\nImported: {imported} records")
    print(f"Updated: {updated} records")
    print(f"\nFinal data (sorted by 期別 descending):")
    
    cursor.execute("SELECT * FROM history ORDER BY 期別 DESC")
    rows = cursor.fetchall()
    for row in rows:
        print(f"  {row}")
    
    conn.close()

if __name__ == '__main__':
    db_path = Path(__file__).parent / 'lotto-539.db'
    
    # Import both CSV files
    import_csv_to_db(Path(__file__).parent / '今彩539_2022.csv', db_path)
    print("\n" + "="*60 + "\n")
    import_csv_to_db(Path(__file__).parent / '今彩539_2023.csv', db_path)
    
    print("\n✅ All data imported successfully!")
