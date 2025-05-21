from flask import Blueprint, jsonify, request, send_file
from app.models.product_sku import ProductSKU
from app.models.product_spu import ProductSPU
from app.retrival_search.image_retrival_search import search_top_k_return_ids
from app.retrival_search.semantic_search import search_optimized_12_5
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

        # Tìm kiếm ảnh, trả về list dict {'product_spu_id', 'score'}
        results = search_top_k_return_ids(
            query_image_path=image_path,  # nhớ truyền đường dẫn file đã lưu
            top_k=100
        )

        # Xóa ảnh tạm thời
        os.remove(image_path)

        if not results:
            return jsonify({'products': [], 'total_items': 0})

        # Lấy danh sách product_spu_id
        spu_ids = [r['product_spu_id'] for r in results]

        # Query sản phẩm
        products = ProductSPU.query.filter(
            ProductSPU.products_spu_id.in_(spu_ids),
            ProductSPU.delete_status == 'Active'
        ).all()

        # Map product_spu_id -> điểm similarity
        score_map = {r['product_spu_id']: r['score'] for r in results}

        # Tạo list dict sản phẩm kèm điểm similarity, loại bỏ sản phẩm không có điểm (nếu có)
        products_with_score = []
        for p in products:
            score = score_map.get(p.products_spu_id)
            if score is not None:
                products_with_score.append({
                    'product': p.to_home(),
                    'score': score
                })

        # Sắp xếp theo điểm similarity giảm dần
        products_sorted = sorted(products_with_score, key=lambda x: x['score'], reverse=True)

        # Trả về JSON chỉ danh sách sản phẩm (không trả score nếu không cần)
        return jsonify({
            'products': [item['product'] for item in products_sorted],
            'total_items': len(products_sorted)
        })
@product_bp.route('/semantic-search', methods=["POST"])
def semantic_search():
    data = request.get_json()
    query = data.get('query')
    page = int(data.get('page', 1))
    top_k = int(data.get('top_k', 50))
    min_similarity = float(data.get('min_similarity', 0.80))

    if not query:
        return jsonify({'error': 'No query provided'}), 400

    # Gọi hàm tìm kiếm semantic
    results = search_optimized_12_5(query, top_k=top_k, page=page, min_similarity=min_similarity)
    if not results:
        return jsonify({'products': [], 'total_items': 0})

    spu_ids = [r['product_spu_id'] for r in results]
    score_map = {r['product_spu_id']: r['score'] for r in results}

    # Lấy dữ liệu từ DB
    products = ProductSPU.query.filter(
        ProductSPU.products_spu_id.in_(spu_ids),
        ProductSPU.delete_status == 'Active'
    ).all()

    # Gắn điểm và sắp xếp
    products_with_score = [
        {'product': p.to_home(), 'score': score_map.get(p.products_spu_id)}
        for p in products if p.products_spu_id in score_map
    ]
    products_sorted = sorted(products_with_score, key=lambda x: x['score'], reverse=True)

    return jsonify({
        'products': [item['product'] for item in products_sorted],
        'total_items': len(products_sorted)
    })