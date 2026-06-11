import os
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
        db = g._database = sqlite3.connect(str(DATABASE))
        db.row_factory = sqlite3.Row
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
