# app/routes/auth.py
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required
from app.models import User
from app.models import db

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()

        if user and user.password == password:
            login_user(user)
            flash("Giriş başarılı!", "success")
            return redirect(url_for('home.dashboard'))
        else:
            flash("Kullanıcı adı veya şifre hatalı!", "danger")
            return redirect(url_for('auth.login'))

    return render_template("auth/login.html")


@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash("Başarıyla çıkış yaptınız.", "info")
    return redirect(url_for('auth.login'))
