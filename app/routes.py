from flask import Blueprint, render_template, redirect, url_for, send_file, request, session, current_app
from datetime import datetime
from io import BytesIO
from urllib.parse import parse_qs, unquote, urlparse
import csv
import re

import app.utils as utils
import app.services.schema_service as schema
import app.services.profile_service as profile
import app.services.appointment_service as appointment
import app.services.reminder_service as reminder_service
from app.models.documents import Documents

import os

bp = Blueprint('main', __name__)


SPECIALITY_KEYWORDS = {
    "Cardiologist": ["chest pain", "heart", "palpitation", "high bp", "blood pressure", "breathlessness"],
    "Dermatologist": ["skin", "rash", "itch", "acne", "eczema", "allergy skin"],
    "Neurologist": ["headache", "migraine", "dizziness", "numbness", "seizure"],
    "Gastroenterologist": ["stomach", "gastric", "vomit", "nausea", "diarrhea", "constipation", "abdominal"],
    "Endocrinologist": ["thyroid", "sugar", "diabetes", "hormone"],
    "Pediatrician": ["child", "kid", "baby", "infant", "toddler"],
    "Urologist": ["urine", "kidney", "bladder", "burning urination"],
    "Dentist": ["tooth", "teeth", "gum", "dental", "jaw"],
    "Family Physician": ["fever", "cold", "cough", "fatigue", "weakness"]
}

EMERGENCY_KEYWORDS = [
    "severe chest pain",
    "fainting",
    "unconscious",
    "stroke",
    "cannot breathe",
    "blood vomiting",
]


def _build_member_name_map(profile_data, members_data):
    members_data = members_data or []
    name_map = {
        int(profile_data["basic_data"]["id"]): f"{profile_data['basic_data']['first_name']} {profile_data['basic_data']['last_name']}"
    }
    for member in members_data:
        name_map[int(member["id"])] = f"{member['first_name']} {member['last_name']}"
    return name_map


def _load_doctor_suggestions_by_speciality(selected_speciality, limit=3):
    dataset_path = os.path.join(current_app.root_path, "static", "datasets", "doctors_dataset.csv")
    doctors = []
    try:
        with open(dataset_path, newline="", encoding="utf-8") as file:
            reader = csv.reader(file)
            for row in reader:
                if len(row) < 2:
                    continue
                doctor_name, doctor_url = row[0].strip(), row[1].strip()
                parsed_url = urlparse(doctor_url)
                params = parse_qs(parsed_url.query)
                specialisation = unquote(params.get("specialization", [""])[0]).strip()
                if specialisation.lower() == selected_speciality.lower():
                    doctors.append({"name": doctor_name, "url": doctor_url})
                if len(doctors) >= limit:
                    break
    except Exception as e:
        print(f"Error loading doctor suggestions: {e}")
    return doctors


def _get_suggested_speciality(response):
    normalized = re.sub(r"\s+", " ", response.lower()).strip()
    if any(keyword in normalized for keyword in EMERGENCY_KEYWORDS):
        return "emergency"

    scores = {}
    for speciality, keywords in SPECIALITY_KEYWORDS.items():
        score = sum(1 for keyword in keywords if keyword in normalized)
        if score:
            scores[speciality] = score

    if not scores:
        return "Family Physician"
    return max(scores, key=scores.get)


def _refresh_session(profile_id):
    profile_data = profile.get_profile(profile_id)
    if not profile_data:
        return False

    session["profile_data"] = profile_data
    session["appointment_data"] = appointment.get_all_appointments(profile_id) or []
    session["members_data"] = profile.get_members(profile_id) or []
    session["upcoming_appointments"] = appointment.get_upcoming_appointments(profile_id, datetime.today())
    session["medication_reminders"] = reminder_service.get_medication_reminders(profile_id)
    session["today_medication_notifications"] = reminder_service.get_today_medication_notifications(profile_id)

    greetings = utils.greetings()
    current_date = datetime.today().strftime("%Y-%m-%d")
    account_created_on = profile_data["stats"]["account_created_on"]
    account_age = datetime.strptime(current_date, "%Y-%m-%d") - datetime.strptime(str(account_created_on), "%Y-%m-%d")
    account_age = str(account_age).split(",")
    completion_percentage = utils.profile_completion(profile_data)
    session["session_stats"] = {
        "greetings": greetings,
        "account_age": account_age[0],
        "completion_percentage": completion_percentage
    }
    return True


# Home
@bp.route("/")
def home():
    schema.check_schema()
    
    session_folder = current_app.config.get('SESSION_FILE_DIR')
    if not session_folder:
        session_folder = os.path.join(current_app.instance_path, 'flask_session')
    
    if os.path.exists(session_folder):
        for filename in os.listdir(session_folder):
            file_path = os.path.join(session_folder, filename)
            try:
                os.remove(file_path)
            except Exception as e:
                print(f"Error deleting session file {file_path}: {e}")
    session.clear()
    return render_template("home.html")


# Đăng ký
@bp.route("/register", methods=['GET', 'POST'])
def register():
    if request.method == "POST":
        profile_data = {
            'first_name': request.form.get("first-name").capitalize(),
            'last_name': request.form.get("last-name").capitalize(),
            'birth_date': request.form.get("birth-date"),
            'gender': request.form.get("gender"),
            'city': request.form.get("city").capitalize(),
            'state': request.form.get("state").capitalize(),
            'email': request.form.get("email-address"),
            'mobile': request.form.get("mobile-number"),
            'password': request.form.get("password"),
            're_password': request.form.get("re-enter-password"),
            'user_category': request.form.get("user-category"),
            'speciality': request.form.get("doctor-speciality"),
            'is_doctor': False
        }

        if profile_data['password'] == profile_data['re_password']:
            if profile_data['user_category'] == 'Normal':
                profile.create_profile(profile_data)
            elif profile_data['user_category'] == 'Doctor':
                profile_data['is_doctor'] = True
                profile.create_profile(profile_data)
            else:
                return render_template("register.html", message="Loại tài khoản không hợp lệ")
            return render_template("login.html", message="Đăng ký thành công")
        else:
            return render_template("register.html", message="Mật khẩu không khớp")
    else:
        return render_template("register.html")


# Đăng nhập
@bp.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == "POST":
        login_data = {
            'email': request.form.get("user-email"),
            'password': request.form.get("user-password")
        }

        id = profile.authentication(login_data)
        if id:
            if not _refresh_session(id):
                return render_template("login.html", message="Không thể tải hồ sơ của tài khoản này.")
            profile_data = session.get("profile_data")
            if profile_data is not None:
                profile_data["basic_data"]["logged_in"] = True

            session['chat_history'] = {
                "user_id": id,
                "messages": [
                    {
                        "sender": "Bot",
                        "message": "Chào mừng đến với chatbot sức khỏe. Hãy mô tả triệu chứng, tôi sẽ gợi ý chuyên khoa phù hợp.",
                        "timestamp": datetime.now()
                    }
                ]
            }
                
            profile.edit_profile(id, profile_data)
            return redirect(url_for('main.dashboard'))
        else:
            return render_template("login.html", message="Không tìm thấy tài khoản")
    else:
        return render_template("login.html")


# Dashboard
@bp.route("/dashboard")
def dashboard():
    profile_data = session.get("profile_data")
    if not profile_data:
        return redirect(url_for("main.login"))

    return render_template("dashboard.html",
                           profile_data=profile_data,
                           members_data=session.get('members_data'),
                           session_stats=session.get('session_stats'),
                           upcoming_appointments=session.get('upcoming_appointments'),
                           chat_history=session.get('chat_history'),
                           ongoing_booking=session.get('ongoing_booking'),
                           list_of_doctors=session.get('list_of_doctors'),
                           available_slots=session.get('available_slots'),
                           today_medication_notifications=session.get('today_medication_notifications'),
                           member_name_map=_build_member_name_map(
                               profile_data,
                               session.get('members_data')
                           )
                           )


# Dashboard: Search Bác sĩs
@bp.route("/search-doctors", methods=['GET', 'POST'])
def search_doctors():
    if request.method == 'POST':
        mode = request.form.get("appointment-mode")
        member_id = request.form.get("appointment-member")
        city = (request.form.get("appointment-city") or "").capitalize()
        doctor_category = request.form.get("appointment-doctor-category")
        
        member_data = profile.get_profile(member_id)
        
        if mode == 'Hospital':
            session['ongoing_booking'] = {
                "mode": mode,
                "user_id": member_id,
                "user_name": member_data["basic_data"]["first_name"] + ' ' + member_data["basic_data"]["last_name"],
                "appointment_city": city,
                "specialist": doctor_category
            }
        elif mode == 'Home':
            session['ongoing_booking'] = {
                "mode": mode,
                "user_id": member_id,
                "user_name": member_data["basic_data"]["first_name"] + ' ' + member_data["basic_data"]["last_name"],
                "appointment_address": member_data["basic_data"]["address"],
                "appointment_city": member_data["basic_data"]["city"],
                "appointment_state": member_data["basic_data"]["state"],
                "specialist": doctor_category
            }
        else:
            session['ongoing_booking'] = {
                "mode": mode,
                "user_id": member_id,
                "user_name": member_data["basic_data"]["first_name"] + ' ' + member_data["basic_data"]["last_name"],
                "appointment_address": "Virtual",
                "appointment_city": "Virtual",
                "appointment_state": "Virtual",
                "specialist": doctor_category 
            }
        
        ongoing_booking = session.get('ongoing_booking')
        session['list_of_doctors'] = profile.get_doctors(mode, ongoing_booking['appointment_city'], doctor_category)
        
    return redirect(url_for('main.dashboard'))


# Dashboard: Check Appointment Availability
@bp.route("/check-availability", methods=['GET', 'POST'])
def check_availability():
    if request.method == 'POST':
        selected_doctor = request.form.get("appointment-doctor")
        appointment_date = request.form.get("appointment-date")

        session['available_slots'] = appointment.check_availability(selected_doctor, appointment_date)
        
        ongoing_booking = session.get('ongoing_booking')
        for doctor in session.get('list_of_doctors'):
            if doctor['doctor_name'] == selected_doctor:
                ongoing_booking['doctor_id'] = doctor['doctor_id']
        ongoing_booking['doctor_name'] = selected_doctor
        ongoing_booking['appointment_date'] = appointment_date
        
        if ongoing_booking['mode'] == "Hospital":
            doctor_data = profile.get_profile(ongoing_booking['doctor_id'])
            ongoing_booking['appointment_address'] = doctor_data["basic_data"]["address"]
            ongoing_booking['appointment_state'] = doctor_data["basic_data"]["state"]
        
        return redirect(url_for('main.dashboard'))


# Dashboard: Đặt lịch khám
@bp.route("/book-appointment", methods=['GET', 'POST'])
def book_appointment():
    if request.method == 'POST':
        appointment_time = request.form.get("appointment-time")
        ongoing_booking = session.get('ongoing_booking')
        ongoing_booking['appointment_time'] = appointment_time

        profile_data = session.get('profile_data')
        if appointment.create_appointment(ongoing_booking):
            if ongoing_booking['mode'] == 'Virtual':
                profile_data["stats"]["number_of_virtual_appointments"] += 1
            else:
                profile_data["stats"]["number_of_appointments"] += 1
            
            profile.edit_profile(profile_data["basic_data"]["id"], profile_data)
            session.pop('ongoing_booking')
            session.pop('list_of_doctors')
            session.pop('available_slots')
            
            session['upcoming_appointments'] = appointment.get_upcoming_appointments(profile_data['basic_data']['id'], datetime.today())

            return redirect(url_for('main.dashboard'))
        else:
            return redirect(url_for('main.dashboard'))


# Dashboard: Clear Selection
@bp.route("/clear-selection", methods=['GET', 'POST'])
def clear_selection():
    if session.get('ongoing_booking'):
        session.pop('ongoing_booking')
    elif session.get('list_of_doctors'):
        session.pop('list_of_doctors')
    elif session.get('available_slots'):
        session.pop('available_slots')
    return redirect(url_for('main.dashboard'))


# Communicate
@bp.route("/communicate", methods=['GET', 'POST'])
def communicate():
    profile_data = session.get("profile_data")
    if not profile_data:
        return redirect(url_for("main.login"))

    if request.method == 'POST':
        appointment_member = request.form.get('appointment-member')
        communication_mode = request.form.get('communication-mode')

    return render_template("communicate.html", 
                           profile_data=profile_data
                           )


# Hồ sơ
@bp.route("/profile")
def view_profile():
    profile_data = session.get("profile_data")
    if not profile_data:
        return redirect(url_for("main.login"))

    profile_id = profile_data["basic_data"]["id"]
    _refresh_session(profile_id)
    profile_data = session.get("profile_data")
    members_data = session.get("members_data") or []
    
    members_appointment_data = []
    for member in members_data:
        members_appointment_data.append(
            {
                'id': member['id'],
                'name': member['first_name'] + ' ' + member['last_name'],
                'appointments': appointment.get_all_appointments(member['id'])
            }
        )

    member_documents_map = {}
    for member in members_data:
        member_documents_map[member["id"]] = profile.get_documents_by_user(member["id"])
    
    return render_template("profile.html", 
                           profile_data=profile_data,
                           members_data=members_data,
                           members_appointment_data=members_appointment_data,
                           appointment_data=session.get('appointment_data'), 
                           session_stats=session.get('session_stats'),
                           medication_reminders=session.get('medication_reminders'),
                           member_documents_map=member_documents_map,
                           member_name_map=_build_member_name_map(profile_data, members_data)
                           )


# Hồ sơ: Thêm thành viên
@bp.route("/add-member", methods=['GET', 'POST'])
def add_member():
    profile_data = session.get('profile_data')
    if request.method == 'POST':
        member_data = {
            'first_name': request.form.get("first-name").capitalize(),
            'last_name': request.form.get("last-name").capitalize(),
            'birth_date': request.form.get("birth-date"),
            'gender': request.form.get("gender"),
            'city': request.form.get("city").capitalize(),
            'state': request.form.get("state").capitalize(),
            'email': request.form.get("email-address"),
            'mobile': request.form.get("mobile-number"),
            'relation': request.form.get("user-relation"),
            'is_doctor': False
        }

        if profile.create_profile(member_data):
            if profile.create_relation(profile_data["basic_data"]["id"], member_data["email"], member_data["relation"]):
                if profile_data["stats"]["number_of_members_added"] >= 0:
                    profile_data["stats"]["number_of_members_added"] += 1
                    profile.edit_profile(profile_data["basic_data"]["id"], profile_data)
                _refresh_session(profile_data["basic_data"]["id"])
                return redirect(url_for('main.view_profile'))
            else:
                return redirect(url_for('main.add_member'))
        else:
            return redirect(url_for('main.add_member'))
    else:   
        return render_template("add_member.html", profile_data=profile_data)


# Hồ sơ: Tải lên Tài liệu y tế
@bp.route("/upload-documents", methods=['GET', 'POST'])
def upload_documents():
    profile_data = session.get('profile_data')
    if not profile_data:
        return redirect(url_for('main.login'))

    if request.method == 'POST':
        file_name = (request.form.get("document-name") or "").strip().capitalize()
        file = request.files['document']
        target_member_id = request.form.get("document-owner") or str(profile_data["basic_data"]["id"])

        if not file or not file_name:
            return redirect(url_for('main.view_profile'))

        try:
            target_member_id = int(target_member_id)
        except ValueError:
            return redirect(url_for('main.view_profile'))

        admin_id = profile_data["basic_data"]["id"]
        if not profile.is_self_or_member(admin_id, target_member_id):
            return redirect(url_for('main.view_profile'))

        if profile.insert_document(file, file_name, target_member_id):
            profile_data["stats"]["number_of_documents_uploaded"] += 1
            profile.edit_profile(admin_id, profile_data)
            _refresh_session(admin_id)
            return redirect(url_for('main.view_profile'))
        return redirect(url_for('main.view_profile'))
    return redirect(url_for('main.view_profile'))


# Hồ sơ: View Tài liệu y tế
@bp.route("/view-document", methods=['POST'])
def view_documents():
    document_id = request.form.get('document-button')
    # Redirect to the GET endpoint to serve the document
    return redirect(url_for('main.get_document', document_id=document_id))


# Hồ sơ: Get Document
@bp.route("/get-document/<document_id>", methods=['GET'])
def get_document(document_id):
    profile_data = session.get('profile_data')
    if not profile_data:
        return redirect(url_for('main.login'))

    document = Documents.query.filter_by(id=document_id).first()
    if not document:
        return redirect(url_for('main.view_profile'))

    admin_id = profile_data["basic_data"]["id"]
    if not profile.is_self_or_member(admin_id, document.user_id):
        return redirect(url_for('main.view_profile'))

    return send_file(
        BytesIO(document.document),
        mimetype='application/pdf',
        as_attachment=False,
        download_name=document.document_name
    )


# Cập nhật hồ sơ
@bp.route("/update-profile", methods=['GET', 'POST'])
def update_profile():
    return render_template("update_profile.html", profile_data=session.get('profile_data'))


# Cập nhật hồ sơ: Update Basic Data
@bp.route("/update-basic-data", methods=['GET', 'POST'])
def update_basic_data():
    if request.method == 'POST':
        profile_data = session.get('profile_data')
        
        profile_data['basic_data']['profile_picture'] = request.files['profile-picture'].read()
        profile_data['basic_data']['first_name'] = request.form.get('first-name').capitalize()
        profile_data['basic_data']['last_name'] = request.form.get('last-name').capitalize()
        profile_data['basic_data']['birth_date'] = request.form.get("birth-date")
        profile_data['basic_data']['address'] = request.form.get("address").title()
        profile_data['basic_data']['city'] = request.form.get("city").capitalize()
        profile_data['basic_data']['state'] = request.form.get("state").capitalize()
        profile_data['basic_data']['mobile_number'] = request.form.get("mobile-number")

        if profile_data["basic_data"]["speciality"] is not None:
            profile_data["basic_data"]["speciality"] = request.form.get("doctor-speciality")

        if not profile.edit_profile(profile_data["basic_data"]["id"], profile_data):
            return None

        return redirect(url_for('main.update_profile'))


# Cập nhật hồ sơ: Update Health Data
@bp.route("/update-health-data", methods=['GET', 'POST'])
def update_health_data():
    if request.method == 'POST':
        profile_data = session.get('profile_data')
        
        profile_data["health_data"]["gender"] = request.form.get("gender")
        profile_data["health_data"]["blood_group"] = request.form.get("blood-group")
        profile_data["health_data"]["weight"] = request.form.get("weight")
        profile_data["health_data"]["height"] = request.form.get("height")
        profile_data["health_data"]["disability"] = request.form.get("disability")
        profile_data["health_data"]["fitzpatrick"] = request.form.get("fitzpatrick-skin-type")
        profile_data["health_data"]["allergies"] = request.form.get("allergies")
        profile_data["health_data"]["cancer"] = request.form.get("cancer")
        profile_data["health_data"]["diabetes"] = request.form.get("diabetes")
        profile_data["health_data"]["thyroid"] = request.form.get("thyroid")
        profile_data["health_data"]["covid"] = request.form.get("covid")
        profile_data["health_data"]["asthma"] = request.form.get("asthma")
        profile_data["health_data"]["hiv_aids"] = request.form.get("hiv-aids")
        profile_data["health_data"]["addiction"] = request.form.get("addiction")
        
        profile.edit_profile(profile_data["basic_data"]["id"], profile_data)

        return redirect(url_for('main.update_profile'))


# Cập nhật hồ sơ: Update Đăng nhập Data
@bp.route("/update-login-data", methods=['GET', 'POST'])
def update_login_data():
    if request.method == "POST":
        profile_data = session.get('profile_data')
        
        profile_data["basic_data"]["email"] = request.form.get("email-address")
        password = request.form.get("password")
        re_enter_password = request.form.get("re-enter-password")

        if password == re_enter_password:
            profile_data["basic_data"]["password"] = password
            profile.edit_profile(profile_data["basic_data"]["id"], profile_data)

        return redirect(url_for('main.update_profile'))


# Medication Reminders: Add
@bp.route("/add-medication-reminder", methods=["POST"])
def add_medication_reminder():
    profile_data = session.get("profile_data")
    if not profile_data:
        return redirect(url_for("main.login"))

    admin_id = int(profile_data["basic_data"]["id"])
    member_id = request.form.get("member-id") or str(admin_id)
    medicine_name = (request.form.get("medicine-name") or "").strip()
    notes = (request.form.get("medicine-notes") or "").strip()
    morning_enabled = request.form.get("morning") == "on"
    evening_enabled = request.form.get("evening") == "on"

    try:
        member_id = int(member_id)
    except ValueError:
        return redirect(url_for("main.view_profile"))

    if not profile.is_self_or_member(admin_id, member_id):
        return redirect(url_for("main.view_profile"))

    if not medicine_name:
        return redirect(url_for("main.view_profile"))
    if not morning_enabled and not evening_enabled:
        return redirect(url_for("main.view_profile"))

    reminder_service.create_medication_reminder(
        {
            "admin_user_id": admin_id,
            "member_id": member_id,
            "medicine_name": medicine_name,
            "notes": notes,
            "morning_enabled": morning_enabled,
            "evening_enabled": evening_enabled,
        }
    )
    _refresh_session(admin_id)
    return redirect(url_for("main.view_profile"))


# Medication Reminders: Xóa
@bp.route("/delete-medication-reminder/<int:reminder_id>", methods=["POST"])
def delete_medication_reminder(reminder_id):
    profile_data = session.get("profile_data")
    if not profile_data:
        return redirect(url_for("main.login"))

    admin_id = int(profile_data["basic_data"]["id"])
    reminder_service.delete_medication_reminder(admin_id, reminder_id)
    _refresh_session(admin_id)
    return redirect(url_for("main.view_profile"))


# Healthcare Chatbot
@bp.route("/healthcare-chatbot", methods=['GET', 'POST'])
def healthcare_chatbot():
    if request.method == 'POST':
        response = (request.form.get('user-response') or "").strip()
        if not response:
            return redirect(url_for('main.dashboard'))

        chat_history = session.get('chat_history')
        if not chat_history:
            chat_history = {
                "user_id": session.get("profile_data", {}).get("basic_data", {}).get("id"),
                "messages": []
            }
        
        message = {
            "sender": "User",
            "message": response,
            "timestamp": datetime.now()
        }
        
        chat_history['messages'].append(message)
        suggested_speciality = _get_suggested_speciality(response)

        if suggested_speciality == "emergency":
            bot_reply = (
                "Phát hiện triệu chứng nghiêm trọng. Vui lòng đến cơ sở cấp cứu ngay "
                "hoặc gọi số cấp cứu địa phương."
            )
            chat_history["messages"].append(
                {
                    "sender": "Bot",
                    "message": bot_reply,
                    "timestamp": datetime.now()
                }
            )
            session["chat_history"] = chat_history
            return redirect(url_for("main.dashboard"))

        doctors = _load_doctor_suggestions_by_speciality(suggested_speciality)
        if doctors:
            doctor_names = ", ".join(doctor["name"] for doctor in doctors)
            doctor_reply = f"Gợi ý bác sĩ ({suggested_speciality}): {doctor_names}."
        else:
            doctor_reply = f"Gợi ý chuyên khoa: {suggested_speciality}. Vui lòng vào mục Đặt lịch khám để tìm bác sĩ phù hợp."

        triage_reply = (
            f"Đánh giá sơ bộ: {suggested_speciality}. "
            "Nội dung này không thay thế chẩn đoán y khoa."
        )
        chat_history["messages"].append(
            {
                "sender": "Bot",
                "message": triage_reply,
                "timestamp": datetime.now()
            }
        )
        chat_history["messages"].append(
            {
                "sender": "Bot",
                "message": doctor_reply,
                "timestamp": datetime.now()
            }
        )

        session["chat_history"] = chat_history
        return redirect(url_for('main.dashboard'))
    return redirect(url_for('main.dashboard'))
