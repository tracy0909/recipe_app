from flask import render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user

from . import auth_bp
from .forms import LoginForm, RegisterForm
from extensions import db
from models import User


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm(request.form)
    if request.method == "POST" and form.validate():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            flash("登入成功", "success")
            next_url = request.args.get("next") or url_for("main.dashboard")
            return redirect(next_url)
        flash("帳號或密碼錯誤", "danger")
    return render_template("auth/login.html", form=form)


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    form = RegisterForm(request.form)
    if request.method == "POST" and form.validate():
        exists = User.query.filter((User.username == form.username.data) | (User.email == form.email.data)).first()
        if exists:
            flash("使用者名稱或 Email 已存在", "warning")
            return render_template("auth/register.html", form=form)

        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash("註冊成功，請登入", "success")
        return redirect(url_for("auth.login"))
    return render_template("auth/register.html", form=form)


@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("已登出", "info")
    return redirect(url_for("main.index"))
