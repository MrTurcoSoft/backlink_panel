# app/models.py
from datetime import datetime,UTC
from app import db
from flask_login import UserMixin

class User(UserMixin, db.Model):
    __tablename__ = "user"
    __table_args__ = {"extend_existing": True}  # 🔧 Çakışmayı engeller
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)

class Setting(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(64), unique=True, nullable=False)
    value = db.Column(db.Text)

class ProductKeyword(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    keyword = db.Column(db.String(255), nullable=False)
    language = db.Column(db.String(10), nullable=True)

class UserProfile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128))
    email = db.Column(db.String(128))
    phone = db.Column(db.String(64))

class ManualSite(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String(512), unique=True, nullable=False)
    keyword = db.Column(db.String(255))
    language = db.Column(db.String(255))
    page_rank = db.Column(db.Float, nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(UTC))

class Log(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    site_url = db.Column(db.String(512))
    status = db.Column(db.String(64))
    screenshot = db.Column(db.String(256))
    timestamp = db.Column(db.DateTime, default=lambda: datetime.now(UTC))

class DiscoveredSite(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String(512), unique=True, nullable=False)
    keyword = db.Column(db.String(256))
    language = db.Column(db.String(10))
    page_rank = db.Column(db.Float)
    has_comment_form = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(UTC))


class ScheduledTask(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    keyword = db.Column(db.String(255), nullable=False)
    language = db.Column(db.String(10), nullable=False, default='de')
    pages = db.Column(db.Integer, default=5)
    interval_minutes = db.Column(db.Integer, default=60)
    last_run = db.Column(db.DateTime)
    is_active = db.Column(db.Boolean, default=True)

class CommentLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    site_id = db.Column(db.Integer, db.ForeignKey('discovered_site.id'), nullable=True)
    url = db.Column(db.String(512), nullable=False)
    status = db.Column(db.String(50), nullable=False)  # success / failed
    screenshot_path = db.Column(db.String(512))
    timestamp = db.Column(db.DateTime, default=lambda: datetime.now(UTC))
    site = db.relationship('DiscoveredSite', backref=db.backref('logs', lazy=True))

