import tempfile
from pathlib import Path
path = Path(tempfile.gettempdir()) / 'lotto-539.db'
print('temp db path:', path)
print('exists', path.exists())
if path.exists():
    try:
        path.unlink()
        print('deleted temp db')
    except Exception as e:
        print('delete failed:', e)
else:
    print('temp db not found, nothing to delete')
