from app.init_DB import db
from datetime import datetime

class Customer(db.Model):
    __tablename__ = 'customers'

    customer_id = db.Column(db.String(36), primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    email = db.Column(db.String(254), nullable=False, unique=True)
    image = db.Column(db.String(500))
    dob = db.Column(db.Date)
    gender = db.Column(db.Enum('Nam', 'Nữ'), nullable=True)
    account_id = db.Column(db.String(36), db.ForeignKey('accounts.account_id'), nullable=False)
    create_date = db.Column(db.DateTime, default=datetime.utcnow)
    update_date = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


    def to_dict(self):
        return {
            'customer_id': self.customer_id,
            'name': self.name,
            'email': self.email,
            'image': self.image,
            'dob': self.dob.isoformat() if self.dob else None,
            'gender': self.gender,
            'account_id': self.account_id,
            'create_date': self.create_date.isoformat() if self.create_date else None,
            'update_date': self.update_date.isoformat() if self.update_date else None
        }