#!/usr/bin/env python3
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.fetch_lotto539_history import fetch_history_records, save_history
from src.database import DATABASE

def update_database():
    """Fetch latest history records and update database."""
    print(f"Fetching latest records from Taiwan Lottery API...")
    print(f"Database: {DATABASE}")
    
    try:
        # Fetch latest records (default 2 months to now)
        records = fetch_history_records()
        print(f"✓ Fetched {len(records)} records")
        
        # Save to database
        inserted_count = save_history(DATABASE, records)
        print(f"✓ Saved {inserted_count} new records to database")
        
        # Show latest records
        import sqlite3
        conn = sqlite3.connect(str(DATABASE))
        cursor = conn.cursor()
        cursor.execute("""
            SELECT 期別, 開獎日, 大小順序, 頭獎中獎注數 
            FROM history 
            ORDER BY 開獎日 DESC 
            LIMIT 10
        """)
        rows = cursor.fetchall()
        
        print(f"\nLatest 10 records:")
        for row in rows:
            print(f"  期別: {row[0]}, 日期: {row[1]}, 號碼: {row[2]}, 頭獎: {row[3]}")
        
        # Show total count
        cursor.execute("SELECT COUNT(*) FROM history")
        total = cursor.fetchone()[0]
        print(f"\nTotal records in database: {total}")
        
        conn.close()
        
        return True
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

if __name__ == '__main__':
    success = update_database()
    sys.exit(0 if success else 1)
