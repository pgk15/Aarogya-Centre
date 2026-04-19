from datetime import date

from app.database import db


class MedicationReminder(db.Model):
    __tablename__ = 'medication_reminders'

    id = db.Column(db.Integer, primary_key=True)
    admin_user_id = db.Column(db.Integer, nullable=False)
    member_id = db.Column(db.Integer, nullable=False)
    medicine_name = db.Column(db.String(100), nullable=False)
    notes = db.Column(db.String(255))
    morning_enabled = db.Column(db.Boolean, default=True, nullable=False)
    evening_enabled = db.Column(db.Boolean, default=True, nullable=False)
    start_date = db.Column(db.Date, default=date.today, nullable=False)
    end_date = db.Column(db.Date)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
