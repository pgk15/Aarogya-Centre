from __future__ import annotations

import argparse
from pathlib import Path
import sys

from sqlalchemy import text

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from main import create_app  # noqa: E402
from app.database import db  # noqa: E402

# Import models so metadata includes all tables.
from app.models import (  # noqa: F401,E402
    appointment_data,
    basic_data,
    doctor_stats,
    documents,
    health_data,
    medication_reminder,
    members_data,
    user_stats,
)

from scripts import export_seed_sql, seed_database  # noqa: E402


def _ensure_schema(schema: str) -> None:
    """Create schema (Postgres) and set search_path so create_all lands in it."""
    if not schema:
        return

    if db.engine.dialect.name != "postgresql":
        # SQLite doesn't support schemas; ignore.
        return

    # Create schema and set it as first on the search_path.
    db.session.execute(text(f'CREATE SCHEMA IF NOT EXISTS "{schema}";'))
    db.session.execute(text(f'SET search_path TO "{schema}", public;'))
    db.session.commit()


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Bootstrap database: ensure schema, create tables, seed sample data.",
    )
    parser.add_argument(
        "--schema",
        default="public",
        help="PostgreSQL schema name (default: public). Ignored for SQLite.",
    )
    parser.add_argument(
        "--no-seed-data",
        action="store_true",
        help="Only create tables; do not insert seed data.",
    )
    parser.add_argument(
        "--export-sql",
        action="store_true",
        help="Also export seed data SQL to docs/seed_data.sql.",
    )

    args = parser.parse_args()

    app = create_app()
    with app.app_context():
        # If user keeps default "public", nothing changes; if custom schema, we respect it.
        if args.schema and args.schema != "public":
            _ensure_schema(args.schema)

        db.create_all()

        if not args.no_seed_data:
            seed_database.seed()

        # Default behavior: when running without flags, do NOT export SQL.
        # For the "no-args" workflow, use scripts/seed_tables.py.
        if args.export_sql:
            export_seed_sql.main()

    print("Bootstrap DB xong.")


if __name__ == "__main__":
    main()
