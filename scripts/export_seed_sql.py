from __future__ import annotations

from datetime import date
from pathlib import Path
import sys

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from scripts.seed_database import SEED_ROWS  # noqa: E402


def _sql_quote(value):
    if value is None:
        return "NULL"
    if isinstance(value, bool):
        return "TRUE" if value else "FALSE"
    if isinstance(value, (int, float)):
        return str(value)
    if isinstance(value, (date,)):
        return f"'{value.isoformat()}'"
    if isinstance(value, (bytes, bytearray)):
        hex_str = bytes(value).hex()
        return f"'\\\\x{hex_str}'::bytea"
    # string fallback
    text = str(value).replace("'", "''")
    return f"'{text}'"


def _upsert_sql(table: str, pk_col: str, row: dict) -> str:
    cols = list(row.keys())
    col_list = ", ".join(cols)
    values_list = ", ".join(_sql_quote(row[c]) for c in cols)

    # On conflict: update everything except pk.
    set_cols = [c for c in cols if c != pk_col]
    if set_cols:
        set_expr = ", ".join(f"{c}=EXCLUDED.{c}" for c in set_cols)
        on_conflict = f"ON CONFLICT ({pk_col}) DO UPDATE SET {set_expr}"
    else:
        on_conflict = f"ON CONFLICT ({pk_col}) DO NOTHING"

    return f"INSERT INTO {table} ({col_list}) VALUES ({values_list}) {on_conflict};"


def main():
    docs_dir = ROOT_DIR / "docs"
    docs_dir.mkdir(parents=True, exist_ok=True)
    out_path = docs_dir / "seed_data.sql"

    lines: list[str] = []
    lines.append("-- Seed data for ChatBot tu van y te")
    lines.append("-- Idempotent: uses INSERT .. ON CONFLICT .. DO UPDATE")
    lines.append("")

    for table, spec in SEED_ROWS.items():
        pk_col = spec["pk"]
        rows = spec["rows"]
        lines.append(f"-- {table}")
        for row in rows:
            lines.append(_upsert_sql(table, pk_col, row))
        lines.append("")

    out_path.write_text("\n".join(lines).strip() + "\n", encoding="utf-8")
    print(f"Da xuat seed data SQL: {out_path}")


if __name__ == "__main__":
    main()

