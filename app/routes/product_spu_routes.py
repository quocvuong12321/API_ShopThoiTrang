import os
from flask import Blueprint, jsonify
from app.models.product_spu import ProductSPU
from flask import send_from_directory
from sqlalchemy.orm import joinedload
product_bp = Blueprint('product_bp', __name__)

@product_bp.route('/', methods=["GET"])
def get_products_spu():
    products_spu = ProductSPU.get_Random_Products()
    return jsonify([item.to_home() for item in products_spu])

@product_bp.route('/detail/<spu_id>', methods=["GET"])
def get_detail_spu(spu_id):
    spu = ProductSPU.query.options(joinedload(ProductSPU.product_skus),
                                   joinedload(ProductSPU.sku_attrs),
                                   joinedload(ProductSPU.description_attrs),
                                   joinedload(ProductSPU.ratings)).filter_by(products_spu_id=spu_id).first()
    if not spu:
        return jsonify({'error': 'Sản phẩm không tồn tại'}), 404


    return jsonify({
        'spu': spu.to_dict(),
        'description_attrs': [d.to_dict() for d in spu.description_attrs],
        'skus': [s.to_dict() for s in spu.product_skus],
        'sku_attrs': [sk.to_dict() for sk in spu.sku_attrs],
        'ratings': [r.to_dict() for r in spu.ratings]
    })

@product_bp.route('/<category_id>')
def get_products_by_category(category_id):
    products = ProductSPU.filter_products_by_categoryid(category_id)
    return jsonify([item.to_home() for item in products])

