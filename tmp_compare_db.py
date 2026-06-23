import sqlite3, tempfile, os
from pathlib import Path
root = Path('lotto-539.db').resolve()
temp = Path(tempfile.gettempdir()) / 'lotto-539.db'
print('root_db', root, 'exists', root.exists(), 'size', root.stat().st_size if root.exists() else 'no')
print('temp_db', temp, 'exists', temp.exists(), 'size', temp.stat().st_size if temp.exists() else 'no')
for name, path in [('root', root), ('temp', temp)]:
    if path.exists():
        try:
            conn = sqlite3.connect(path)
            cur = conn.cursor()
            cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in cur.fetchall()]
            print(name, 'tables', tables)
            for t in tables:
                try:
                    cur.execute(f"SELECT COUNT(*) FROM '{t}'")
                    print('  ', t, cur.fetchone()[0])
                except Exception as ex:
                    print('  ', t, 'ERROR', ex)
            conn.close()
        except Exception as ex:
            print(name, 'ERROR', ex)
