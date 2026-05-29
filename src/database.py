import sqlite3
from flask import g
from .utils import parse_numbers

DATABASE = 'lotto-539.db'

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
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
