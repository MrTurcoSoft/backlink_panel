# app/routes/home.py
from flask import Blueprint, render_template
from flask_login import login_required, current_user

home_bp = Blueprint('home', __name__)

@home_bp.route('/')
@login_required
def index():
    return render_template("home/index.html")

@home_bp.route('/dashboard')
@login_required
def dashboard():
    return render_template("home/dashboard.html", user=current_user)
