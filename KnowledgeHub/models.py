from flask_login import UserMixin
from app import db
from uuid import uuid4
from sqlalchemy.sql import func
from datetime import datetime
import pytz  # For timezone handling

IST = pytz.timezone('Asia/Kolkata')

class Course(db.Model):
    id = db.Column(db.String(), primary_key=True, default=lambda: str(uuid4()))
    course_name = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=False)
    price = db.Column(db.Float, nullable=False)
    course_image = db.Column(db.String(255))
    created_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(IST))
    updated_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(IST),
                           onupdate=lambda: datetime.now(IST))
    
    # Relationship to purchase records
    purchases = db.relationship('Purchase', backref='course', lazy=True)

    def __repr__(self):
        return f'<Course {self.course_name}>'

class User(db.Model, UserMixin):
    uid = db.Column(db.String(), primary_key=True, default=lambda: str(uuid4()))
    username = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), nullable=False, unique=True, index=True)
    password = db.Column(db.String, nullable=False)
    role = db.Column(db.String, default='user')
    description = db.Column(db.String)
    
    # Relationship to purchase records
    purchases = db.relationship('Purchase', backref='user', lazy=True)

    def __repr__(self):
        return f'<User {self.username}, {self.email}, Role {self.role}>'
    
    def get_id(self):
        return self.uid

class Purchase(db.Model):
    id = db.Column(db.String(), primary_key=True, default=lambda: str(uuid4()))
    user_id = db.Column(db.String(), db.ForeignKey('user.uid'), nullable=False)
    course_id = db.Column(db.String(), db.ForeignKey('course.id'), nullable=False)
    purchased_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(IST))
    # Optionally add more fields, e.g. payment_status, transaction_id, etc.

    def __repr__(self):
        return f'<Purchase User:{self.user_id} Course:{self.course_id}>'
