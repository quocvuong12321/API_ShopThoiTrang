import os
from flask import Blueprint, jsonify, request
from app.models.product_sku import ProductSKU
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
    # Lấy giá trị min_price và max_price từ query string (nếu có)
    min_price = request.args.get('min_price', type=float)
    max_price = request.args.get('max_price', type=float)

    # Lọc sản phẩm theo category_id
    products = ProductSPU.filter_products_by_categoryid(category_id)

    # Nếu có min_price và max_price, thêm điều kiện lọc theo giá
    if min_price is not None and max_price is not None:
        products = [product for product in products if ProductSKU.get_price_by_spu_id(product.products_spu_id) >= min_price and ProductSKU.get_price_by_spu_id(product.products_spu_id) <= max_price]

    # Trả về kết quả dưới dạng JSON
    return jsonify([item.to_home() for item in products])
