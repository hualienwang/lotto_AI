import sqlite3
import os
path = os.path.abspath('lotto-539.db')
print('DB', path)
conn = sqlite3.connect(path)
cur = conn.cursor()
cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = [row[0] for row in cur.fetchall()]
print('tables =', tables)
for t in tables:
    try:
        cur.execute(f'SELECT COUNT(*) FROM "{t}"')
        print(t, cur.fetchone()[0])
    except Exception as e:
        print(t, 'ERROR', e)
conn.close()