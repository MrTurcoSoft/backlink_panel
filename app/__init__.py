# __init__.py

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from werkzeug.security import generate_password_hash
from pymysql import OperationalError
import pymysql
import logging

# MySQLdb olarak pymysql kullanma
pymysql.install_as_MySQLdb()

# Uygulama bileşenleri
db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'

def create_app():
    app = Flask(__name__)
    app.config.from_object('config.Config')  # Config ayarlarını ekleyin

    # Uygulama bileşenlerini başlat
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)

    # Kullanıcı yükleyici
    @login_manager.user_loader
    def load_user(user_id):
        from app.models import User  # User modelini burada içe aktarın
        return User.query.get(int(user_id))

    # Blueprint'leri kaydet
    from app.routes.auth import auth_bp
    from app.routes.google import google_bp
    from app.routes.home import home_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(google_bp)
    app.register_blueprint(home_bp)

    # Veritabanı tablolarını oluştur ve admin kullanıcısını ekle
    with app.app_context():
        db.create_all()  # Tabloları oluştur
        create_admin_user(app)

    # SQLAlchemy log seviyesini ayarla
    setup_logging()

    return app

def create_admin_user(app):
    """Admin kullanıcısını oluştur."""
    from app.models import User  # User modelini burada içe aktarın
    try:
        if not User.query.filter_by(username="admin").first():
            admin = User(username="admin", password=generate_password_hash("Asli281019*Cagdas"))
            db.session.add(admin)
            db.session.commit()
    except OperationalError as e:
        app.logger.error(f"Database connection failed: {str(e)}")

def setup_logging():
    """Logging ayarlarını yapılandır."""
    logging.basicConfig()
    logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)
