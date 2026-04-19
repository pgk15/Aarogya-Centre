from pathlib import Path
import sys

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from main import create_app  # noqa: E402
from app.database import db  # noqa: E402

# Import models so SQLAlchemy metadata includes all tables.
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


def main():
    app = create_app()
    with app.app_context():
        db.create_all()
        print("Da tao schema (toan bo bang) tren DB hien tai.")


if __name__ == "__main__":
    main()

