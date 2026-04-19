
CREATE TABLE basic_data (
	id SERIAL NOT NULL, 
	profile_picture BYTEA, 
	first_name VARCHAR(25), 
	last_name VARCHAR(25), 
	birth_date DATE, 
	address VARCHAR(100), 
	city VARCHAR(25), 
	state VARCHAR(25), 
	mobile_number BIGINT, 
	email_address VARCHAR(50), 
	password VARCHAR(50), 
	speciality VARCHAR(50), 
	is_doctor BOOLEAN, 
	logged_in BOOLEAN, 
	PRIMARY KEY (id)
)

;


CREATE TABLE doctor_stats (
	id SERIAL NOT NULL, 
	account_created_on DATE, 
	number_of_appointments_diagnosed INTEGER, 
	number_of_virtual_appointments_diagnosed INTEGER, 
	PRIMARY KEY (id)
)

;


CREATE TABLE documents (
	id SERIAL NOT NULL, 
	user_id INTEGER NOT NULL, 
	document_name VARCHAR(50) NOT NULL, 
	document BYTEA NOT NULL, 
	upload_date DATE NOT NULL, 
	PRIMARY KEY (id)
)

;


CREATE TABLE health_data (
	id SERIAL NOT NULL, 
	gender VARCHAR(25), 
	age INTEGER, 
	blood_group VARCHAR(10), 
	weight INTEGER, 
	height INTEGER, 
	obesity VARCHAR(25), 
	disability VARCHAR(50), 
	fitzpatrick VARCHAR(50), 
	allergies VARCHAR(50), 
	diabetes VARCHAR(50), 
	thyroid VARCHAR(50), 
	cancer VARCHAR(50), 
	covid VARCHAR(50), 
	asthma VARCHAR(50), 
	hiv_aids VARCHAR(50), 
	addiction VARCHAR(50), 
	PRIMARY KEY (id)
)

;


CREATE TABLE medication_reminders (
	id SERIAL NOT NULL, 
	admin_user_id INTEGER NOT NULL, 
	member_id INTEGER NOT NULL, 
	medicine_name VARCHAR(100) NOT NULL, 
	notes VARCHAR(255), 
	morning_enabled BOOLEAN NOT NULL, 
	evening_enabled BOOLEAN NOT NULL, 
	start_date DATE NOT NULL, 
	end_date DATE, 
	is_active BOOLEAN NOT NULL, 
	PRIMARY KEY (id)
)

;


CREATE TABLE members_data (
	member_id SERIAL NOT NULL, 
	user_id INTEGER, 
	relation VARCHAR, 
	PRIMARY KEY (member_id)
)

;


CREATE TABLE user_stats (
	id SERIAL NOT NULL, 
	account_created_on DATE, 
	number_of_appointments INTEGER, 
	number_of_virtual_appointments INTEGER, 
	number_of_documents_uploaded INTEGER, 
	number_of_members_added INTEGER, 
	PRIMARY KEY (id)
)

;


CREATE TABLE appointment_data (
	id SERIAL NOT NULL, 
	mode VARCHAR(25), 
	user_id INTEGER, 
	user_name VARCHAR(50), 
	doctor_id INTEGER, 
	doctor_name VARCHAR(50), 
	specialist VARCHAR(50), 
	appointment_date DATE, 
	appointment_time VARCHAR(25), 
	appointment_address VARCHAR(100), 
	appointment_city VARCHAR(25), 
	appointment_state VARCHAR(25), 
	PRIMARY KEY (id), 
	FOREIGN KEY(user_id) REFERENCES basic_data (id), 
	FOREIGN KEY(doctor_id) REFERENCES basic_data (id)
)

;
