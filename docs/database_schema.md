# Database Schema (PostgreSQL)

Duoc tao tu SQLAlchemy models trong project.

## appointment_data

| Cot | Kieu du lieu | Null | Mac dinh |
|---|---|---|---|
| id | INTEGER | NO | nextval('appointment_data_id_seq'::regclass) |
| mode | VARCHAR(25) | YES |  |
| user_id | INTEGER | YES |  |
| user_name | VARCHAR(50) | YES |  |
| doctor_id | INTEGER | YES |  |
| doctor_name | VARCHAR(50) | YES |  |
| specialist | VARCHAR(50) | YES |  |
| appointment_date | DATE | YES |  |
| appointment_time | VARCHAR(25) | YES |  |
| appointment_address | VARCHAR(100) | YES |  |
| appointment_city | VARCHAR(25) | YES |  |
| appointment_state | VARCHAR(25) | YES |  |

- Primary key: id
- Foreign key: doctor_id -> basic_data(id)
- Foreign key: user_id -> basic_data(id)

## basic_data

| Cot | Kieu du lieu | Null | Mac dinh |
|---|---|---|---|
| id | INTEGER | NO | nextval('basic_data_id_seq'::regclass) |
| profile_picture | BYTEA | YES |  |
| first_name | VARCHAR(25) | YES |  |
| last_name | VARCHAR(25) | YES |  |
| birth_date | DATE | YES |  |
| address | VARCHAR(100) | YES |  |
| city | VARCHAR(25) | YES |  |
| state | VARCHAR(25) | YES |  |
| mobile_number | BIGINT | YES |  |
| email_address | VARCHAR(50) | YES |  |
| password | VARCHAR(50) | YES |  |
| speciality | VARCHAR(50) | YES |  |
| is_doctor | BOOLEAN | YES |  |
| logged_in | BOOLEAN | YES |  |

- Primary key: id
- Foreign key: (none)

## doctor_stats

| Cot | Kieu du lieu | Null | Mac dinh |
|---|---|---|---|
| id | INTEGER | NO | nextval('doctor_stats_id_seq'::regclass) |
| account_created_on | DATE | YES |  |
| number_of_appointments_diagnosed | INTEGER | YES |  |
| number_of_virtual_appointments_diagnosed | INTEGER | YES |  |

- Primary key: id
- Foreign key: (none)

## documents

| Cot | Kieu du lieu | Null | Mac dinh |
|---|---|---|---|
| id | INTEGER | NO | nextval('documents_id_seq'::regclass) |
| user_id | INTEGER | NO |  |
| document_name | VARCHAR(50) | NO |  |
| document | BYTEA | NO |  |
| upload_date | DATE | NO |  |

- Primary key: id
- Foreign key: (none)

## health_data

| Cot | Kieu du lieu | Null | Mac dinh |
|---|---|---|---|
| id | INTEGER | NO | nextval('health_data_id_seq'::regclass) |
| gender | VARCHAR(25) | YES |  |
| age | INTEGER | YES |  |
| blood_group | VARCHAR(10) | YES |  |
| weight | INTEGER | YES |  |
| height | INTEGER | YES |  |
| obesity | VARCHAR(25) | YES |  |
| disability | VARCHAR(50) | YES |  |
| fitzpatrick | VARCHAR(50) | YES |  |
| allergies | VARCHAR(50) | YES |  |
| diabetes | VARCHAR(50) | YES |  |
| thyroid | VARCHAR(50) | YES |  |
| cancer | VARCHAR(50) | YES |  |
| covid | VARCHAR(50) | YES |  |
| asthma | VARCHAR(50) | YES |  |
| hiv_aids | VARCHAR(50) | YES |  |
| addiction | VARCHAR(50) | YES |  |

- Primary key: id
- Foreign key: (none)

## medication_reminders

| Cot | Kieu du lieu | Null | Mac dinh |
|---|---|---|---|
| id | INTEGER | NO | nextval('medication_reminders_id_seq'::regclass) |
| admin_user_id | INTEGER | NO |  |
| member_id | INTEGER | NO |  |
| medicine_name | VARCHAR(100) | NO |  |
| notes | VARCHAR(255) | YES |  |
| morning_enabled | BOOLEAN | NO |  |
| evening_enabled | BOOLEAN | NO |  |
| start_date | DATE | NO |  |
| end_date | DATE | YES |  |
| is_active | BOOLEAN | NO |  |

- Primary key: id
- Foreign key: (none)

## members_data

| Cot | Kieu du lieu | Null | Mac dinh |
|---|---|---|---|
| member_id | INTEGER | NO | nextval('members_data_member_id_seq'::regclass) |
| user_id | INTEGER | YES |  |
| relation | VARCHAR | YES |  |

- Primary key: member_id
- Foreign key: (none)

## user_stats

| Cot | Kieu du lieu | Null | Mac dinh |
|---|---|---|---|
| id | INTEGER | NO | nextval('user_stats_id_seq'::regclass) |
| account_created_on | DATE | YES |  |
| number_of_appointments | INTEGER | YES |  |
| number_of_virtual_appointments | INTEGER | YES |  |
| number_of_documents_uploaded | INTEGER | YES |  |
| number_of_members_added | INTEGER | YES |  |

- Primary key: id
- Foreign key: (none)
