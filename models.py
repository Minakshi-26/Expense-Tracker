#-----------------------models.py-----------------------
from extensions import db
from flask_login import UserMixin
from datetime import datetime


# ---------------- main user model ko create kia ---------------- #
class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)   
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(10), default='User')   
    budget = db.Column(db.Float, default=0.0)         

    expenses = db.relationship('Expense', backref='user', lazy=True)

    def __repr__(self):
        return f"<User {self.username} - {self.email}>"

# ---------------- Expense model creation ---------------- #
class Expense(db.Model):
    __tablename__ = 'expenses'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=True)   
    description = db.Column(db.String(200), nullable=True)  
    amount = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(50), nullable=False)
    date = db.Column(db.Date, default=datetime.utcnow)

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    def __repr__(self):
        return f"<Expense {self.category} - ₹{self.amount}>"

# ---------------- REPORT MODEL ---------------- #
class Report(db.Model):
    __tablename__ = 'reports'

    id = db.Column(db.Integer, primary_key=True)
    month = db.Column(db.String(20), nullable=False)   
    total_expense = db.Column(db.Float, default=0.0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    def __repr__(self):
        return f"<Report {self.month} - ₹{self.total_expense}>"





