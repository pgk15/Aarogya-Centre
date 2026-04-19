from pathlib import Path
import sys

from sqlalchemy import inspect
from sqlalchemy.dialects import postgresql
from sqlalchemy.schema import CreateTable

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from main import create_app
from app.database import db

# Ensure all models are imported so metadata includes every table.
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

DOCS_DIR = ROOT_DIR / "docs"
SCHEMA_MD = DOCS_DIR / "database_schema.md"
SCHEMA_SQL = DOCS_DIR / "database_schema.sql"


def write_schema_markdown(engine):
    inspector = inspect(engine)
    tables = sorted(inspector.get_table_names())

    lines = [
        "# Database Schema (PostgreSQL)",
        "",
        "Duoc tao tu SQLAlchemy models trong project.",
        "",
    ]

    for table_name in tables:
        lines.append(f"## {table_name}")
        lines.append("")
        lines.append("| Cot | Kieu du lieu | Null | Mac dinh |")
        lines.append("|---|---|---|---|")

        for col in inspector.get_columns(table_name):
            default = col.get("default")
            lines.append(
                f"| {col['name']} | {col['type']} | {'YES' if col.get('nullable') else 'NO'} | {default if default is not None else ''} |"
            )

        pk = inspector.get_pk_constraint(table_name).get("constrained_columns", [])
        fks = inspector.get_foreign_keys(table_name)
        lines.append("")
        lines.append(f"- Primary key: {', '.join(pk) if pk else '(none)'}")
        if fks:
            for fk in fks:
                local_cols = ", ".join(fk.get("constrained_columns", []))
                ref_table = fk.get("referred_table")
                ref_cols = ", ".join(fk.get("referred_columns", []))
                lines.append(f"- Foreign key: {local_cols} -> {ref_table}({ref_cols})")
        else:
            lines.append("- Foreign key: (none)")
        lines.append("")

    SCHEMA_MD.write_text("\n".join(lines), encoding="utf-8")


def write_schema_sql():
    ddl_statements = []
    for table in db.metadata.sorted_tables:
        ddl = str(CreateTable(table).compile(dialect=postgresql.dialect()))
        ddl_statements.append(f"{ddl};")

    SCHEMA_SQL.write_text("\n\n".join(ddl_statements) + "\n", encoding="utf-8")


def main():
    app = create_app()
    with app.app_context():
        db.create_all()
        DOCS_DIR.mkdir(parents=True, exist_ok=True)
        write_schema_markdown(db.engine)
        write_schema_sql()
        print("Da tao/cap nhat toan bo bang tren DB hien tai.")
        print(f"- Schema markdown: {SCHEMA_MD}")
        print(f"- Schema SQL: {SCHEMA_SQL}")


if __name__ == "__main__":
    main()
