from flask import Blueprint, jsonify, request, send_file
from app.models.product_sku import ProductSKU
from app.models.product_spu import ProductSPU
from app.models.image_retrival_search import search_top_k_return_ids
from sqlalchemy.orm import joinedload
import os

product_bp = Blueprint('product_bp', __name__)

@product_bp.route('/', methods=["GET"])
def get_List_Products():
    page = int(request.args.get('page', 1))
    per_page=50
    min_price = request.args.get('min_price', type=float)
    max_price = request.args.get('max_price', type=float)
    category_id = request.args.get('category_id', type=str)

    query = ProductSPU.query.filter_by(delete_status='Active')

    if category_id:
        query = query.filter_by(category_id=category_id)

    if min_price is not None and max_price is not None:
        query = query.join(ProductSKU).filter(ProductSKU.price >= min_price, ProductSKU.price <= max_price)

    query = query.order_by(ProductSPU.create_date.desc())

    products = query.offset((page - 1) * per_page).limit(per_page).all()

    total_items = query.count()

    total_pages = (total_items + per_page - 1) // per_page

    return jsonify({'products' : [item.to_home() for item in products],
                   'total_items': total_items,
                   'total_pages': total_pages,
                   'current_page': page,
                   'per_page': per_page})

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


@product_bp.route('/image-search', methods=["POST"])
def image_search():
    if request.method == 'POST':
        file = request.files.get('file')
        if not file:
            return jsonify({'error': 'No file provided'}), 400
        
        # Lưu tạm thời ảnh
        uploads_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'uploads'))
        os.makedirs(uploads_dir, exist_ok=True)  

        image_path = os.path.join(uploads_dir, file.filename)
        file.save(image_path)

        # Tìm kiếm ảnh
        result_ids = search_top_k_return_ids(
            query_image_path=file,
            top_k=100
        )
        # Xóa ảnh tạm thời
        os.remove(image_path)

        if not result_ids:
            return jsonify({'products': [], 'total_items': 0})

        # Lấy dữ liệu sản phẩm theo result_ids
        products = ProductSPU.query.filter(
        ProductSPU.products_spu_id.in_(result_ids),
        ProductSPU.delete_status == 'Active'
        ).all()
        return jsonify({
        'products': [p.to_home() for p in products],
        'total_items': len(products)
    })
