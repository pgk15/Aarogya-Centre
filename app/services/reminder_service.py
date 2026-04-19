from datetime import date

from app.database import db
from app.models.medication_reminder import MedicationReminder


MORNING_TIME_LABEL = "08:00 AM"
EVENING_TIME_LABEL = "08:00 PM"


def create_medication_reminder(data):
    try:
        reminder = MedicationReminder(
            admin_user_id=data["admin_user_id"],
            member_id=data["member_id"],
            medicine_name=data["medicine_name"],
            notes=data.get("notes"),
            morning_enabled=data.get("morning_enabled", True),
            evening_enabled=data.get("evening_enabled", True),
            start_date=data.get("start_date", date.today()),
            end_date=data.get("end_date"),
            is_active=True
        )
        db.session.add(reminder)
        db.session.commit()
        return True
    except Exception as e:
        db.session.rollback()
        print(f"Error creating medication reminder: {e}")
        return False


def get_medication_reminders(admin_user_id):
    try:
        reminders = MedicationReminder.query.filter_by(
            admin_user_id=admin_user_id,
            is_active=True
        ).order_by(MedicationReminder.id.desc()).all()
        return [
            {
                "id": reminder.id,
                "admin_user_id": reminder.admin_user_id,
                "member_id": reminder.member_id,
                "medicine_name": reminder.medicine_name,
                "notes": reminder.notes,
                "morning_enabled": reminder.morning_enabled,
                "evening_enabled": reminder.evening_enabled,
                "start_date": reminder.start_date,
                "end_date": reminder.end_date,
                "is_active": reminder.is_active,
            }
            for reminder in reminders
        ]
    except Exception as e:
        print(f"Error fetching medication reminders: {e}")
        return []


def delete_medication_reminder(admin_user_id, reminder_id):
    try:
        reminder = MedicationReminder.query.filter_by(
            id=reminder_id,
            admin_user_id=admin_user_id
        ).first()
        if not reminder:
            return False
        reminder.is_active = False
        db.session.commit()
        return True
    except Exception as e:
        db.session.rollback()
        print(f"Error deleting medication reminder: {e}")
        return False


def get_today_medication_notifications(admin_user_id, current_date=None):
    current_date = current_date or date.today()
    reminders = get_medication_reminders(admin_user_id)
    notifications = []

    for reminder in reminders:
        if reminder["start_date"] and reminder["start_date"] > current_date:
            continue
        if reminder["end_date"] and reminder["end_date"] < current_date:
            continue

        if reminder["morning_enabled"]:
            notifications.append({
                "member_id": reminder["member_id"],
                "medicine_name": reminder["medicine_name"],
                "time_label": MORNING_TIME_LABEL
            })
        if reminder["evening_enabled"]:
            notifications.append({
                "member_id": reminder["member_id"],
                "medicine_name": reminder["medicine_name"],
                "time_label": EVENING_TIME_LABEL
            })

    return notifications
