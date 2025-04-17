from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from app.config import Config
from flask import request, jsonify
import cloudinary
import cloudinary.uploader

# Cấu hình Cloudinary từ config
cloudinary.config(
    cloud_name=Config.CLOUDINARY_CLOUD_NAME,
    api_key=Config.CLOUDINARY_API_KEY,
    api_secret=Config.CLOUDINARY_API_SECRET
)

# Khởi tạo ứng dụng Flask
app = Flask(__name__)

# Cấu hình Flask với Config
app.config.from_object(Config)

# Khởi tạo SQLAlchemy với Flask app
db = SQLAlchemy(app)

# Định nghĩa mô hình (model)
class images_test(db.Model):
    __tablename__ = 'images_test'

    id = db.Column(db.Integer, primary_key=True)
    image_path = db.Column(db.String(500), nullable = False)





@app.route('/upload_image', methods=['POST'])
def upload_image():
    if 'image' not in request.files:
        return jsonify({'error': 'No image part'}), 400

    file = request.files['image']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    try:
        # Upload lên Cloudinary
        upload_result = cloudinary.uploader.upload(
        file,
        public_id=file.filename,    
        use_filename=True,          
        unique_filename=False,     
        overwrite=True
        )
        image_url = upload_result['secure_url']

        # Lưu vào DB
        new_image = images_test(image_path=image_url)
        db.session.add(new_image)
        db.session.commit()

        return jsonify({
            'message': 'Upload thành công!',
            'image_url': image_url
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
