# Tong Quan
Aarogya Centre la nen tang cham soc suc khoe toan dien, giup nguoi dung quan ly thong tin suc khoe ca nhan va gia dinh, dat lich kham, tu van voi chatbot, va tuong tac voi bac si qua hinh thuc trực tuyến.

## Cong Nghe Su Dung
- Frontend: HTML, CSS, JavaScript, Bootstrap, Jinja
- Backend: Flask
- Co so du lieu: PostgreSQL (ho tro chay local bang SQLite fallback)
- Chatbot: NLP + xu ly tu khoa
- Goi trực tuyến: WebRTC

## Tinh Nang Chinh
1. Quan ly ho so ca nhan va thong tin suc khoe.
2. Them thanh vien gia dinh va dat lich cho tung thanh vien.
3. Luu tru tai lieu y te (don thuoc, ket qua xet nghiem, benh an).
4. Chatbot ho tro tu van co ban va goi y chuyen khoa.
5. Dat lich kham truc tiep/online va theo doi lich hen sap toi.
6. Nhac uong thuoc theo 2 moc co dinh: sang va chieu.

## Hinh Anh Minh Hoa
### Dang nhap
![Login](./docs/login.png)

### Dashboard
![Dashboard-1](./docs/dashboard-1.png)
![Dashboard-2](./docs/dashboard-2.png)

### Chatbot
![Chatbot](./docs/chatbot.png)

### Ho so
![Profile-1](./docs/profile-1.png)
![Profile-2](./docs/profile-2.png)

# Cai Dat
## Yeu Cau
- Python 3.8+
- PostgreSQL (neu chay production)
- Node.js

## Cac Buoc
1. Clone repo:
```sh
git clone https://github.com/PrathameshLakawade/Aarogya-Centre.git
```

2. Tao virtual environment va cai dependency:
```sh
python -m venv venv
source venv/bin/activate  # Windows: venv\\Scripts\\activate
pip install -r requirements.txt
```

3. Tao file `.env`:
```sh
# Database (PostgreSQL local)
DATABASE_URL='postgresql+psycopg2://postgres@localhost:5432/chatbot'
# Hoac dung DB_*:
# DB_HOST='localhost'
# DB_PORT='5432'
# DB_NAME='chatbot'
# DB_USER='postgres'
# DB_PASSWORD=''

# Mail
MAIL_SERVER='your-email-server'
MAIL_PORT='587'
MAIL_USERNAME='your-email-address'
MAIL_PASSWORD='your-password'
MAIL_USE_TLS='true'
MAIL_USE_SSL='false'
```

4. Tao bang tren PostgreSQL + xuat schema:
```sh
python3 scripts/setup_postgres.py
```
Script se:
- Tao toan bo bang theo models.
- Xuat "sheet schema" vao:
  - `docs/database_schema.md`
  - `docs/database_schema.sql`

5. Chay server:
```sh
python3 main.py
```

# Cach Su Dung
1. Dang ky/Dang nhap tai khoan.
2. Cap nhat ho so ca nhan.
3. Them thanh vien gia dinh.
4. Tai len tai lieu y te cho ban than hoac thanh vien.
5. Dat lich kham theo hinh thuc Hospital/Home/Virtual.
6. Su dung chatbot de nhan goi y chuyen khoa.
7. Tao nhac uong thuoc sang/chieu va theo doi tren dashboard.

# Huong Phat Trien Tiep
- Tich hop thiet bi deo thong minh theo doi suc khoe.
- Nang cap chatbot voi mo hinh AI manh hon.
- Ho tro e-prescription va thanh toan.

# Giay Phep
Du an su dung giay phep MIT.
