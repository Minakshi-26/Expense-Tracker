from flask import Flask, render_template
from extensions import db, login_manager, bcrypt
import os
import logging

def create_app():
    app = Flask(__name__)

    # Secure Config
    app.config['SECRET_KEY'] = os.getenv("SECRET_KEY", "supersecretkey123")
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///expenses.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # File Upload Config
    app.config['UPLOAD_FOLDER'] = os.path.join(os.getcwd(), "uploads")
    app.config['REPORT_FOLDER'] = os.path.join(os.getcwd(), "reports")

    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(app.config['REPORT_FOLDER'], exist_ok=True)

    # Init Extensions
    db.init_app(app)
    login_manager.init_app(app)
    bcrypt.init_app(app)

    login_manager.login_view = "main.login"
    login_manager.login_message_category = "info"

    # Register Blueprints
    from routes import main_routes
    app.register_blueprint(main_routes)

    # User Loader 
    from models import User
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Logging Setup
    logging.basicConfig(
        filename="error.log",
        level=logging.ERROR,
        format="%(asctime)s [%(levelname)s] %(message)s",
    )

    return app

# 👇 Global app (Render ko yahi chahiye)
app = create_app()

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))






