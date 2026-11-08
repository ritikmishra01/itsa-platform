import os
import sqlite3

def audit_sqlite():
    db_path = os.path.abspath('instance/itsa_platform.db')
    root_db = os.path.abspath('itsa_platform.db')
    
    print(f"instance/itsa_platform.db: exists={os.path.exists(db_path)}, size={os.path.getsize(db_path)} bytes")
    print(f"root itsa_platform.db: exists={os.path.exists(root_db)}, size={os.path.getsize(root_db)} bytes")
    
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("PRAGMA integrity_check;")
    print("Integrity check:", cur.fetchall())
    
    cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [r[0] for r in cur.fetchall() if not r[0].startswith('sqlite_')]
    print(f"\nTables found in instance/itsa_platform.db ({len(tables)}):")
    total_rows = 0
    for t in sorted(tables):
        cur.execute(f'SELECT COUNT(*) FROM "{t}";')
        cnt = cur.fetchone()[0]
        total_rows += cnt
        print(f"  {t:28}: {cnt} rows")
    print(f"\nTotal records: {total_rows}")
    conn.close()

if __name__ == '__main__':
    audit_sqlite()
