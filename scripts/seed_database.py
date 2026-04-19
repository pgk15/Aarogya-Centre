from datetime import date
from pathlib import Path
import sys

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from main import create_app
from app.database import db
from app.models.basic_data import BasicData
from app.models.health_data import HealthData
from app.models.user_stats import UserStats
from app.models.doctor_stats import DoctorStats
from app.models.members_data import MembersData
from app.models.appointment_data import AppointmentData
from app.models.documents import Documents
from app.models.medication_reminder import MedicationReminder


# Seed definition lives here so it can be reused to export SQL.
# Keep values compatible with model columns (English internal enums for logic).
SEED_ROWS = {
    "basic_data": {
        "pk": "id",
        "rows": [
            {
                "id": 1,
                "first_name": "Khiem",
                "last_name": "Pham",
                "birth_date": date(2000, 1, 1),
                "address": "123 Nguyen Trai",
                "city": "Ho Chi Minh",
                "state": "Ho Chi Minh",
                "mobile_number": 912345678,
                "email_address": "khiem@gmail.com",
                "password": "123456",
                "speciality": None,
                "is_doctor": False,
                "logged_in": False,
            },
            {
                "id": 2,
                "first_name": "Lan",
                "last_name": "Pham",
                "birth_date": date(2005, 6, 15),
                "address": "123 Nguyen Trai",
                "city": "Ho Chi Minh",
                "state": "Ho Chi Minh",
                "mobile_number": 934567890,
                "email_address": "lan.member@gmail.com",
                "password": "123456",
                "speciality": None,
                "is_doctor": False,
                "logged_in": False,
            },
            {
                "id": 10,
                "first_name": "An",
                "last_name": "Nguyen",
                "birth_date": date(1985, 3, 1),
                "address": "45 Le Loi",
                "city": "Ho Chi Minh",
                "state": "Ho Chi Minh",
                "mobile_number": 988111222,
                "email_address": "dr.an@gmail.com",
                "password": "123456",
                "speciality": "Family Physician",
                "is_doctor": True,
                "logged_in": False,
            },
            {
                "id": 11,
                "first_name": "Bao",
                "last_name": "Tran",
                "birth_date": date(1988, 7, 10),
                "address": "88 Tran Hung Dao",
                "city": "Ho Chi Minh",
                "state": "Ho Chi Minh",
                "mobile_number": 977333444,
                "email_address": "dr.bao@gmail.com",
                "password": "123456",
                "speciality": "Cardiologist",
                "is_doctor": True,
                "logged_in": False,
            },
        ],
    },
    "health_data": {
        "pk": "id",
        "rows": [
            {
                "id": 1,
                "gender": "Male",
                "age": 26,
                "blood_group": "O+",
                "weight": 68,
                "height": 172,
                "obesity": "No",
                "disability": "No",
                "fitzpatrick": "Type 3",
                "allergies": "None",
                "diabetes": "No",
                "thyroid": "No",
                "cancer": "No",
                "covid": "No",
                "asthma": "No",
                "hiv_aids": "No",
                "addiction": "No",
            },
            {
                "id": 2,
                "gender": "Female",
                "age": 21,
                "blood_group": "A+",
                "weight": 52,
                "height": 160,
                "obesity": "No",
                "disability": "No",
                "fitzpatrick": "Type 3",
                "allergies": "Pollen",
                "diabetes": "No",
                "thyroid": "No",
                "cancer": "No",
                "covid": "No",
                "asthma": "No",
                "hiv_aids": "No",
                "addiction": "No",
            },
        ],
    },
    "user_stats": {
        "pk": "id",
        "rows": [
            {
                "id": 1,
                "account_created_on": date.today(),
                "number_of_appointments": 1,
                "number_of_virtual_appointments": 1,
                "number_of_documents_uploaded": 1,
                "number_of_members_added": 1,
            },
            {
                "id": 2,
                "account_created_on": date.today(),
                "number_of_appointments": 0,
                "number_of_virtual_appointments": 0,
                "number_of_documents_uploaded": 0,
                "number_of_members_added": 0,
            },
        ],
    },
    "doctor_stats": {
        "pk": "id",
        "rows": [
            {
                "id": 10,
                "account_created_on": date.today(),
                "number_of_appointments_diagnosed": 10,
                "number_of_virtual_appointments_diagnosed": 5,
            },
            {
                "id": 11,
                "account_created_on": date.today(),
                "number_of_appointments_diagnosed": 8,
                "number_of_virtual_appointments_diagnosed": 3,
            },
        ],
    },
    "members_data": {
        "pk": "member_id",
        "rows": [
            {
                "member_id": 2,
                "user_id": 1,
                "relation": "Sister",
            },
        ],
    },
    "appointment_data": {
        "pk": "id",
        "rows": [
            {
                "id": 1001,
                "mode": "Virtual",
                "user_id": 1,
                "user_name": "Khiem Pham",
                "doctor_id": 10,
                "doctor_name": "An Nguyen",
                "specialist": "Family Physician",
                "appointment_date": date.today(),
                "appointment_time": "10:00",
                "appointment_address": "Virtual",
                "appointment_city": "Virtual",
                "appointment_state": "Virtual",
            },
        ],
    },
    "documents": {
        "pk": "id",
        "rows": [
            {
                "id": 2001,
                "user_id": 1,
                "document_name": "Ket qua xet nghiem mau",
                "document": b"Sample document bytes",
                "upload_date": date.today(),
            },
        ],
    },
    "medication_reminders": {
        "pk": "id",
        "rows": [
            {
                "id": 3001,
                "admin_user_id": 1,
                "member_id": 1,
                "medicine_name": "Vitamin D",
                "notes": "Sau an",
                "morning_enabled": True,
                "evening_enabled": True,
                "start_date": date.today(),
                "end_date": None,
                "is_active": True,
            },
        ],
    },
}


def upsert(model, identity, values):
    row = db.session.get(model, identity)
    if row is None:
        row = model(**values)
        db.session.add(row)
    else:
        for key, value in values.items():
            setattr(row, key, value)


def seed():
    db.create_all()

    model_map = {
        "basic_data": (BasicData, "id"),
        "health_data": (HealthData, "id"),
        "user_stats": (UserStats, "id"),
        "doctor_stats": (DoctorStats, "id"),
        "members_data": (MembersData, "member_id"),
        "appointment_data": (AppointmentData, "id"),
        "documents": (Documents, "id"),
        "medication_reminders": (MedicationReminder, "id"),
    }

    for table, spec in SEED_ROWS.items():
        model, pk_col = model_map[table]
        for row in spec["rows"]:
            upsert(model, row[pk_col], row)

    db.session.commit()


def main():
    app = create_app()
    with app.app_context():
        seed()
        print("Seed du lieu thanh cong.")


if __name__ == "__main__":
    main()
