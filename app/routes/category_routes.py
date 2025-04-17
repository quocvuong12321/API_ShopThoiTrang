from flask import Blueprint, jsonify
from app.models.category import Category

category_bp = Blueprint('category_bp', __name__)

@category_bp.route('/', methods=["GET"])
def get_categories():
    categories = Category.get_10categories()
    return jsonify([c.name for c in categories])