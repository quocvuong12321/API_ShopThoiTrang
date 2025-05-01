from app.init_DB import db
from sqlalchemy.sql.expression import func

class DescriptionAttr(db.Model):
    __tablename__ = 'description_attr'

    description_attr_id = db.Column(db.String(36), primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    value = db.Column(db.String(500), nullable=False)
    products_spu_id = db.Column(db.String(36), db.ForeignKey('products_spu.products_spu_id'), nullable=False)

    def to_dict(self):
        return {
            'attr_id' : self.description_attr_id,
            'name': self.name,
            'value': self.value
        }