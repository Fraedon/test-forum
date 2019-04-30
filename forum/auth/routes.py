from flask import flash, redirect, render_template, url_for
from flask_login import login_user, logout_user
from werkzeug.wrappers.response import Response

from forum import db
from forum.auth import auth_bp
from forum.auth.forms import LoginForm, RegisterForm
from forum.models import User


@auth_bp.route("/register", methods=["GET", "POST"])
def register() -> Response:
    form = RegisterForm()
    if form.validate_on_submit():
        # Create the new user
        # noinspection PyArgumentList
        user = User(display_name=form.display_name.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()

        # Log the user in
        login_user(user)

        # Show a success message, then redirect
        flash("Registered successfully")
        return redirect(url_for("main.index"))

    return render_template("auth/register.html", form=form)


@auth_bp.route("/login", methods=["GET", "POST"])
def login() -> Response:
    form = LoginForm()
    if form.validate_on_submit():
        # Log the user in
        user = User.query.filter_by(email=form.email.data).first()
        login_user(user)

        # Show a success message, then redirect
        flash("Logged in successfully")
        return redirect(url_for("board.boards"))

    return render_template("auth/login.html", form=form)


@auth_bp.route("/logout", methods=["GET"])
def logout() -> Response:
    # Log the user out
    logout_user()

    # Show a success message, then redirect
    flash("Logged out successfully")
    return redirect(url_for("main.index"))
