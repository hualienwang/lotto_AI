import os
import shutil
import sqlite3
import tempfile
from pathlib import Path

from flask import g

from .utils import parse_numbers

DATABASE = Path(os.environ.get('LOTTO_DB_PATH', Path(tempfile.gettempdir()) / 'lotto-539.db'))


def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        DATABASE.parent.mkdir(parents=True, exist_ok=True)
        
        # Check if we need to initialize the temp database from the pre-populated template in the project root
        need_copy = not DATABASE.exists() or DATABASE.stat().st_size == 0
        if not need_copy:
            try:
                temp_conn = sqlite3.connect(str(DATABASE))
                cursor = temp_conn.cursor()
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='history'")
                if not cursor.fetchone():
                    need_copy = True
                temp_conn.close()
            except Exception:
                need_copy = True

        if need_copy:
            project_db = Path(__file__).resolve().parent.parent / 'lotto-539.db'
            if project_db.exists() and project_db.stat().st_size > 0:
                try:
                    shutil.copy2(project_db, DATABASE)
                except Exception:
                    pass

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
