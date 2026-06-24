import os
import sqlite3
from pathlib import Path

from flask import g

from .utils import parse_numbers

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATABASE = Path(os.environ.get('LOTTO_DB_PATH', PROJECT_ROOT / 'lotto-539.db'))


def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        DATABASE.parent.mkdir(parents=True, exist_ok=True)

        db = g._database = sqlite3.connect(str(DATABASE))
        db.row_factory = sqlite3.Row
        
        # Ensure the history table exists to prevent sqlite3.OperationalError
        try:
            db.execute("""
                CREATE TABLE IF NOT EXISTS history (
                    "期別" TEXT PRIMARY KEY,
                    "開獎日" TEXT NOT NULL,
                    "大小順序" TEXT NOT NULL,
                    "頭獎中獎注數" INTEGER NOT NULL
                )
            """)
            db.commit()
        except Exception:
            pass
            
    return db

def load_draws():
    db = get_db()
    rows = db.execute(
        'SELECT "期別", "大小順序", "開獎日" FROM history ORDER BY "期別" DESC'
    ).fetchall()
    return [
        {
            'period': row['期別'],
            'numbers': parse_numbers(row['大小順序']),
            'draw_date': row['開獎日']
        }
        for row in rows
    ]
