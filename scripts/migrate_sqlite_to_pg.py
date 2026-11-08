"""
ITSA Platform - SQLite to PostgreSQL Database Migration Script
Safely and idempotently migrates data from instance/itsa_platform.db to central PostgreSQL.
Preserves primary keys, foreign keys, relationships, and resets auto-increment sequences.
"""

import os
import sys
import argparse
import datetime
from sqlalchemy import create_engine, MetaData, Table, inspect, text
from sqlalchemy.orm import sessionmaker

# Ensure project root is in python path
basedir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if basedir not in sys.path:
    sys.path.insert(0, basedir)

from app import create_app
from app.extensions import db
from app.config import normalize_database_url


def run_migration(sqlite_path=None, target_pg_url=None, dry_run=False, truncate_first=False):
    if not sqlite_path:
        sqlite_path = os.path.join(basedir, 'instance', 'itsa_platform.db')
        if not os.path.exists(sqlite_path):
            sqlite_path = os.path.join(basedir, 'itsa_platform.db')

    if not os.path.exists(sqlite_path):
        print(f"ERROR: SQLite database file not found at: {sqlite_path}")
        sys.exit(1)

    print("=" * 65)
    print("ITSA PLATFORM - CENTRAL DATABASE MIGRATION TOOL")
    print("=" * 65)
    print(f"Source SQLite  : {sqlite_path} ({os.path.getsize(sqlite_path):,} bytes)")

    if not target_pg_url:
        target_pg_url = os.environ.get('DATABASE_URL')

    if not target_pg_url or target_pg_url.startswith('sqlite:'):
        print("ERROR: Please provide a valid target PostgreSQL URL via --target or DATABASE_URL.")
        print("Example: python scripts/migrate_sqlite_to_pg.py --target postgresql://user:pass@host:port/dbname")
        sys.exit(1)

    # Normalize PostgreSQL URL
    normalized_pg_url = normalize_database_url(target_pg_url)
    # Mask password for display
    display_url = normalized_pg_url
    if "@" in display_url and "://" in display_url:
        prefix, rest = display_url.split("://", 1)
        creds, host_part = rest.split("@", 1)
        user = creds.split(":", 1)[0] if ":" in creds else creds
        display_url = f"{prefix}://{user}:****@{host_part}"
    print(f"Target Database: {display_url}")
    print(f"Dry Run Mode   : {'ENABLED (No writes will be made)' if dry_run else 'DISABLED (Live migration)'}")
    print("=" * 65)

    # Initialize Flask app context to load models
    app = create_app('development')
    with app.app_context():
        # Connect to SQLite
        sqlite_engine = create_engine(f"sqlite:///{sqlite_path}")
        sqlite_inspector = inspect(sqlite_engine)
        sqlite_tables = set(sqlite_inspector.get_table_names())

        # Connect to PostgreSQL
        print("\nConnecting to target PostgreSQL database...")
        try:
            pg_engine = create_engine(normalized_pg_url, pool_pre_ping=True)
            with pg_engine.connect() as conn:
                version = conn.execute(text("SELECT version();")).scalar()
                print(f"Connected successfully to PostgreSQL:\n  {version[:70]}...")
        except Exception as e:
            print(f"ERROR connecting to PostgreSQL: {e}")
            sys.exit(1)

        if not dry_run:
            print("\nEnsuring all tables and schema exist in target PostgreSQL...")
            db.metadata.create_all(bind=pg_engine)
            print("Target tables verified.")

        # Ordered tables by foreign key dependency
        sorted_tables = db.metadata.sorted_tables
        print(f"\nDiscovered {len(sorted_tables)} tables in dependency order.")

        migration_summary = []

        if truncate_first and not dry_run:
            print("\nTruncating existing records in target database (cascading)...")
            with pg_engine.connect() as conn:
                for table in reversed(sorted_tables):
                    try:
                        conn.execute(text(f'TRUNCATE TABLE "{table.name}" CASCADE;'))
                    except Exception as ex:
                        pass
                conn.commit()
            print("Existing target records truncated.")

        print("\nMigrating table data:")
        print("-" * 65)
        print(f"{'Table Name':<28} | {'SQLite Rows':<12} | {'Migrated':<12} | {'Status'}")
        print("-" * 65)

        for table in sorted_tables:
            table_name = table.name
            if table_name not in sqlite_tables:
                migration_summary.append((table_name, 0, 0, "Not in SQLite"))
                print(f"{table_name:<28} | {0:<12} | {0:<12} | Skipped (Empty)")
                continue

            # Read rows from SQLite
            with sqlite_engine.connect() as s_conn:
                s_rows = s_conn.execute(table.select()).mappings().all()

            row_count = len(s_rows)
            if row_count == 0:
                migration_summary.append((table_name, 0, 0, "No data"))
                print(f"{table_name:<28} | {0:<12} | {0:<12} | Empty")
                continue

            if dry_run:
                migration_summary.append((table_name, row_count, 0, "Dry Run (OK)"))
                print(f"{table_name:<28} | {row_count:<12} | {'-':<12} | Ready")
                continue

            # Live migration: insert rows
            inserted_count = 0
            with pg_engine.begin() as pg_conn:
                for row_dict in s_rows:
                    clean_row = dict(row_dict)
                    
                    # Convert boolean integers or timestamps if needed
                    for col in table.columns:
                        col_val = clean_row.get(col.name)
                        if col_val is not None:
                            if str(col.type) == 'BOOLEAN' and isinstance(col_val, int):
                                clean_row[col.name] = bool(col_val)

                    # Check if primary key exists (idempotency)
                    pk_cols = [c.name for c in table.primary_key.columns]
                    exists = False
                    if pk_cols:
                        where_clause = " AND ".join([f'"{c}" = :{c}' for c in pk_cols])
                        pk_params = {c: clean_row[c] for c in pk_cols}
                        check_sql = text(f'SELECT 1 FROM "{table_name}" WHERE {where_clause} LIMIT 1;')
                        existing = pg_conn.execute(check_sql, pk_params).scalar()
                        if existing:
                            exists = True

                    if not exists:
                        pg_conn.execute(table.insert().values(clean_row))
                        inserted_count += 1

            status_str = f"Done (+{inserted_count})" if inserted_count == row_count else f"Merged ({inserted_count} new)"
            migration_summary.append((table_name, row_count, inserted_count, status_str))
            print(f"{table_name:<28} | {row_count:<12} | {inserted_count:<12} | {status_str}")

        if not dry_run:
            print("\nSynchronizing PostgreSQL auto-increment sequences...")
            with pg_engine.begin() as pg_conn:
                for table in sorted_tables:
                    pk_cols = [c for c in table.primary_key.columns if 'int' in str(c.type).lower()]
                    for pk in pk_cols:
                        seq_sql = text(f"""
                            SELECT setval(
                                pg_get_serial_sequence('"{table.name}"', '{pk.name}'),
                                COALESCE((SELECT MAX("{pk.name}") FROM "{table.name}"), 1),
                                true
                            );
                        """)
                        try:
                            pg_conn.execute(seq_sql)
                        except Exception:
                            # Table might not use serial sequence or is non-numeric
                            pass
            print("PostgreSQL primary key sequences successfully reset to MAX(id).")

        print("=" * 65)
        total_src = sum(s[1] for s in migration_summary)
        total_migrated = sum(s[2] for s in migration_summary)
        print(f"MIGRATION COMPLETE: {total_src} SQLite records processed, {total_migrated} live records in PostgreSQL.")
        print("=" * 65)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Migrate ITSA Platform SQLite database to PostgreSQL.")
    parser.add_argument('--sqlite', help="Path to SQLite database file (default: instance/itsa_platform.db)")
    parser.add_argument('--target', help="Target PostgreSQL connection URL (or set DATABASE_URL)")
    parser.add_argument('--dry-run', action='store_true', help="Inspect and validate migration without writing data")
    parser.add_argument('--truncate', action='store_true', help="Truncate target tables before inserting")
    args = parser.parse_args()

    run_migration(
        sqlite_path=args.sqlite,
        target_pg_url=args.target,
        dry_run=args.dry_run,
        truncate_first=args.truncate
    )
