from datetime import datetime
from flask import url_for
from app.init_DB import db
from sqlalchemy.sql.expression import func
from app.models.product_sku import ProductSKU
from app.models.rating import Ratings
class ProductSPU(db.Model):
    __tablename__ = 'products_spu'

    products_spu_id = db.Column(db.String(36), primary_key=True)
    name = db.Column(db.Text, nullable=False)
    brand_id = db.Column(db.String(36), db.ForeignKey('suppliers.supplier_id'), nullable=False)
    description = db.Column(db.Text, nullable=False)
    short_description = db.Column(db.Text, nullable=False)
    stock_status = db.Column(db.Enum('InStock', 'OutOfStock'), default='InStock')
    delete_status = db.Column(db.Enum('Active', 'Deleted'), default='Active')
    sort = db.Column(db.Integer, default=0)
    create_date = db.Column(db.DateTime, default=datetime.utcnow)
    update_date = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    image = db.Column(db.String(500), nullable=False)
    media = db.Column(db.Text)
    key = db.Column(db.String(500), nullable=False, unique=True)
    category_id = db.Column(db.String(36), db.ForeignKey('categorys.category_id'), nullable=False)

    product_skus = db.relationship('ProductSKU', backref='spu', lazy=True)
    description_attrs = db.relationship('DescriptionAttr', backref='spu', lazy=True)
    sku_attrs = db.relationship('ProductSKUAttr', backref='spu', lazy=True)
    ratings = db.relationship('Ratings', backref='spu', lazy=True)
    def to_dict(self):
        rating_data = Ratings.getRatingAndReviewCount(self.products_spu_id)
        return {
            'products_spu_id': self.products_spu_id,
            'name': self.name,
            'price': ProductSKU.get_price_by_spu_id(self.products_spu_id),
            'brand_id': self.brand_id,
            'image': self.image,
            'key': self.key,
            'short_description': self.short_description,
            'description' : self.description,
            'category_id': self.category_id,
            'total_rating': rating_data['total_rating'],
            'average_star':rating_data['avg_star'],
            'media' : self.media
        }
    
    

    def to_home(self):
        rating_data = Ratings.getRatingAndReviewCount(self.products_spu_id)
        image_path = self.image
        static_image_url = f"/static/{image_path}"
        return{
        'product_spu_id' : self.products_spu_id,
        'name': self.name,
        'brand_id': self.brand_id,
        'image': static_image_url,
        'price': ProductSKU.get_price_by_spu_id(self.products_spu_id),
        'total_rating': rating_data['total_rating'],
        'average_star':rating_data['avg_star'],
        'key': self.key,
        }
    
    def get_Random_Products():
        products = ProductSPU.query.order_by(func.rand()).limit(1000).all()
        return products


    def filter_products_by_categoryid(id):
        return ProductSPU.query.filter_by(category_id=id).all()
    
    def filter_product_by_Price(min_price, max_price):
        return (
        ProductSPU.query
        .join(ProductSKU)
        .filter(ProductSKU.price >= min_price, ProductSKU.price <= max_price)
        .distinct(ProductSPU.products_spu_id)  # Đảm bảo chỉ lấy một lần mỗi ProductSPU
        .all()
    )
    


    