

Bước 1: mở terminal nhập lệnh tạo thư viện ảo
python -m venv .venv

Bước 2: Kích hoạt môi trường ảo
.venv\scripts\activate

Bước 3: cài các môi trường cần thiết, đã có trong file requirements.txt
pip install -r requirements.txt

Bước 4: app.config.py
tại SQLALCHEMY_DATABASE_URI
sửa lại chuỗi kết nối đến database của mình

Bước 5: Chạy chương trình
chạy chương trình run.py