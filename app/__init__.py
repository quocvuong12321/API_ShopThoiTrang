import os
from flask import Flask, send_from_directory
# from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from app.routes.category_routes import category_bp
from app.init_DB import db
from app.config import Config  # Import cấu hình từ config.py
from app.routes.product_spu_routes import product_bp  # nếu có



def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)  # Load cấu hình từ Config

    db.init_app(app)  # Khởi tạo db
    CORS(app)  # Kích hoạt CORS



    register_routes(app)

    return app

def register_routes(app):
    app.register_blueprint(category_bp, url_prefix='/categories')
    app.register_blueprint(product_bp, url_prefix='/products')  


# Route để phục vụ ảnh từ folder uploads/
def register_image_route(app):
    @app.route('/uploads/<path:filename>')
    def uploaded_file(filename):
        uploads_dir = os.path.abspath(os.path.join(app.root_path, "..", "uploads"))
        return send_from_directory(uploads_dir, filename)