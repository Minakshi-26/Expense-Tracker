# from app import create_app
# from extensions import db
# from models import User, Expense, Report
# from sqlalchemy import inspect

# app = create_app()

# with app.app_context():
#     # Purani tables hata do (agar pehle galat bani ho)
#     db.drop_all()

#     # Nayi tables create karo
#     db.create_all()

#     # Check karne ke liye list print
#     inspector = inspect(db.engine)
#     print("Tables created:", inspector.get_table_names())
