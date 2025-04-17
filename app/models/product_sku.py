from datetime import datetime
from app.init_DB import db
from sqlalchemy.sql.expression import func
from app.models.description_attr import DescriptionAttr
from app.models.product_sku_attr import ProductSKUAttr


class ProductSKU(db.Model):
    __tablename__ = 'product_skus'

    product_sku_id = db.Column(db.String(36), primary_key=True)
    value = db.Column(db.String(128), nullable=False)
    sku_stock = db.Column(db.Integer, default=0)
    price = db.Column(db.Float, default=0.0)
    sort = db.Column(db.Integer, default=0)
    create_date = db.Column(db.DateTime, default=datetime.utcnow)
    update_date = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    products_spu_id = db.Column(db.String(36), db.ForeignKey('products_spu.products_spu_id'), nullable=False)

    def to_dict(self):
        return {
            'product_sku_id': self.product_sku_id,
            'value': self.value,
            'price': self.price,
            'sku_stock': self.sku_stock
        }
    
    def get_price_by_spu_id(spu_id):
        return ProductSKU.query.filter_by(products_spu_id=spu_id).first().price

