# wsgi.py
from app import create_app, db

app = create_app()

# optional: first run par tables create ho jayein
with app.app_context():
    db.create_all()

if __name__ == "__main__":
        app.run(debug=True)

