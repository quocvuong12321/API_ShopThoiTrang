from app.init_DB import db
from sqlalchemy.sql.expression import func


class ProductSKUAttr(db.Model):
    __tablename__ = 'product_sku_attrs'

    product_sku_attr_id = db.Column(db.String(36), primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    value = db.Column(db.String(500), nullable=False)
    image = db.Column(db.String(500))
    products_spu_id = db.Column(db.String(36), db.ForeignKey('products_spu.products_spu_id'), nullable=False)

    def to_dict(self):
        return {
            'sku_attr_id': self.product_sku_attr_id,
            'name': self.name,
            'value': self.value,
            'image': self.image
        }