"""
Optional Migration Utility: SQLite to PostgreSQL
Usage:
    python scripts/migrate_sqlite_to_postgres.py --sqlite-path itsa_platform.db --postgres-url postgresql+psycopg2://user:pass@host:5432/dbname
"""
import os
import sys
import argparse

sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(__file__))))

from sqlalchemy import create_engine, MetaData
from app import create_app, db

def migrate_data(sqlite_path, postgres_url):
    if not os.path.exists(sqlite_path):
        print(f"[!] SQLite source file not found at: {sqlite_path}")
        sys.exit(1)

    print(f"[*] Reading source SQLite: {sqlite_path}")
    print(f"[*] Target PostgreSQL: {postgres_url.split('@')[-1] if '@' in postgres_url else 'target'}")

    src_engine = create_engine(f"sqlite:///{os.path.abspath(sqlite_path)}")
    dst_engine = create_engine(postgres_url)

    app = create_app('production')
    with app.app_context():
        print("[*] Creating schema on PostgreSQL target...")
        db.metadata.create_all(dst_engine)

    src_meta = MetaData()
    src_meta.reflect(bind=src_engine)

    # Order of tables to respect foreign keys
    table_order = [
        'users', 'student_profiles', 'coordinator_profiles', 'event_categories', 'venues',
        'events', 'event_coordinators', 'event_registrations', 'event_tickets',
        'attendance', 'certificates', 'feedback', 'posts', 'post_media',
        'post_reactions', 'comments', 'comment_replies', 'post_shares', 'saved_posts',
        'hashtags', 'post_hashtags', 'mentions', 'notifications', 'event_gallery',
        'event_volunteers', 'itsa_points', 'reports', 'ai_recommendations',
        'ai_analysis', 'audit_logs'
    ]

    with src_engine.connect() as src_conn, dst_engine.connect() as dst_conn:
        for t_name in table_order:
            if t_name in src_meta.tables:
                src_table = src_meta.tables[t_name]
                rows = src_conn.execute(src_table.select()).fetchall()
                if rows:
                    print(f"  [>] Migrating {len(rows)} records for {t_name}...")
                    insert_stmt = src_table.insert()
                    for r in rows:
                        try:
                            dst_conn.execute(insert_stmt.values(dict(r._mapping)))
                        except Exception as e:
                            print(f"    [!] Warning on row in {t_name}: {e}")
                    dst_conn.commit()
                else:
                    print(f"  [-] {t_name} (0 records)")

    print("[OK] Data migration completed.")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Migrate ITSA Platform SQLite database to PostgreSQL")
    parser.add_argument('--sqlite-path', default='itsa_platform.db', help='Path to local SQLite .db file')
    parser.add_argument('--postgres-url', required=True, help='Destination PostgreSQL connection URL')
    args = parser.parse_args()
    migrate_data(args.sqlite_path, args.postgres_url)
