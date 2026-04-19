from __future__ import annotations

from pathlib import Path
import sys

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

from scripts import export_seed_sql, seed_database, setup_postgres  # noqa: E402


def main() -> None:
    """
    One-shot bootstrap:
    - Connect DB from `.env` / `DATABASE_URL`
    - Create ALL tables (full schema/columns)
    - Seed sample rows for ALL tables
    - Export schema docs + seed SQL for moving to another DB
    """
    app = create_app()
    with app.app_context():
        db.create_all()
        seed_database.seed()

        # Export "sheet schema" + DDL (docs/database_schema.*)
        (ROOT_DIR / "docs").mkdir(parents=True, exist_ok=True)
        setup_postgres.write_schema_markdown(db.engine)
        setup_postgres.write_schema_sql()

        # Export seed SQL (docs/seed_data.sql)
        export_seed_sql.main()

    print("Seed schema + seed data xong.")


if __name__ == "__main__":
    main()

