from app.init_DB import db
from sqlalchemy.sql.expression import func


class Category(db.Model):
    __tablename__ = 'categorys'

    category_id = db.Column(db.String(36), primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    key = db.Column(db.String(128), nullable=False)
    path = db.Column(db.String(128), nullable=False)
    parent = db.Column(db.String(36), db.ForeignKey('categorys.category_id'))

    # Tự động ánh xạ mối quan hệ cha - con
    children = db.relationship('Category', backref=db.backref('parent_category', remote_side=[category_id]))

    def to_dict(self):
        return {
            'category_id': self.category_id,
            'name': self.name,
            'key': self.key,
            'path': self.path,
            'parent': self.parent
        }
    
    def get_10categories():
        categories = Category.query.order_by(func.rand()).limit(10).all()
        return categories