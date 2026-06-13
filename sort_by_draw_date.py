#!/usr/bin/env python3
import sqlite3
from pathlib import Path

def sort_by_draw_date(db_path):
    """Sort records in database by 開獎日 (descending)."""
    print(f"Sorting database {db_path} by 開獎日 (descending)...")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Query sorted by 開獎日 descending
    cursor.execute("""
        SELECT * FROM history 
        ORDER BY 開獎日 DESC, 期別 DESC
    """)
    
    rows = cursor.fetchall()
    print(f"\nTotal records: {len(rows)}")
    print(f"\nTop 10 records (sorted by 開獎日 descending):")
    
    for i, row in enumerate(rows[:10]):
        print(f"  {i+1}. 期別: {row[0]}, 開獎日: {row[1]}, 號碼: {row[2]}, 頭獎: {row[3]}")
    
    print(f"\nBottom 10 records (oldest):")
    for i, row in enumerate(rows[-10:]):
        print(f"  {len(rows)-9+i}. 期別: {row[0]}, 開獎日: {row[1]}, 號碼: {row[2]}, 頭獎: {row[3]}")
    
    conn.close()

if __name__ == '__main__':
    db_path = Path(__file__).parent / 'lotto-539.db'
    sort_by_draw_date(db_path)
    print("\n✅ Sort verification complete!")
