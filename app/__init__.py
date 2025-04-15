from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from pymysql import OperationalError
from werkzeug.security import generate_password_hash

from config import Config
from flask_migrate import Migrate
from sqlalchemy.exc import IntegrityError
import pymysql
import os

pymysql.install_as_MySQLdb()



migrate = Migrate()
db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)

    from app.models import User

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    from app.routes.auth import auth_bp
    from app.routes.google import google_bp
    from app.routes.home import home_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(google_bp)
    app.register_blueprint(home_bp)

    with app.app_context():
        db.create_all()  # Tabloları oluştur
        try:
            if not User.query.filter_by(username="admin").first():
                admin = User(username="admin", password=generate_password_hash("Asli281019*Cagdas"))
                db.session.add(admin)
                db.session.commit()
        except OperationalError as e:
            app.logger.error(f"Database connection failed: {str(e)}")

    import logging
    logging.basicConfig()
    logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)

    return app
