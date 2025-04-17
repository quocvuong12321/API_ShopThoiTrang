from datetime import datetime
from app.init_DB import db
from sqlalchemy.sql.expression import func
from sqlalchemy import func

class Ratings(db.Model):
    __tablename__ = 'ratings'
    rating_id = db.Column(db.String(36),primary_key = True)
    comment = db.Column(db.Text, nullable = False)
    star = db.Column(db.Integer,default=0)
    create_date =db.Column(db.DateTime, default = datetime.utcnow)
    update_date =db.Column(db.DateTime, default = datetime.utcnow,onupdate=datetime.utcnow)
    customer_id = db.Column(db.String(36), db.ForeignKey('customers.customer_id') ,nullable = False)
    products_spu_id = db.Column(db.String(36), db.ForeignKey('products_spu.products_spu_id'), nullable=False)

    customer = db.relationship('Customer', backref='ratings', lazy=True)
    # product = db.relationship('ProductSPU', backref='ratings', lazy=True)
    def to_dict(self):
        return {
            'name': self.customer.name,
            'comment' : self.comment,
            'star': self.star,
            'create_date': self.create_date,
        }
    
    def getRatingAndReviewCount(product_id):
        count = db.session.query(func.count(Ratings.star)).filter_by(products_spu_id=product_id).scalar()
        avg_star = db.session.query(func.sum(Ratings.star) / func.count(Ratings.star)).filter_by(products_spu_id=product_id).scalar()

        count = count or 0
        avg_star = round(avg_star or 0, 2)

        return{
            'total_rating': count,
            'avg_star': avg_star 
        }
    