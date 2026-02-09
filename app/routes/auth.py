"""Authentication routes."""

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import login_required, login_user, logout_user

from app.forms import LoginForm
from app.models import get_or_create_session_user, remove_session_user
from app.services.samba import SambaError, authenticate_user

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    form_valid = form.validate_on_submit()
    if request.method == "POST":
        print(f"[DEBUG AUTH] POST received, form valid: {form_valid}")
        if not form_valid:
            print(f"[DEBUG AUTH] Form errors: {form.errors}")
    if form_valid:
        username = form.username.data
        password = form.password.data
        print(f"[DEBUG AUTH] Attempting login for user: {username}")
        try:
            result = authenticate_user(username, password)
            print(f"[DEBUG AUTH] authenticate_user returned: {result}")
            if result:
                user = get_or_create_session_user(username)
                login_user(user)
                next_page = request.args.get("next")
                flash("Logged in successfully.", "success")
                return redirect(next_page or url_for("dashboard.index"))
            else:
                flash("Invalid username or password.", "danger")
        except SambaError as e:
            print(f"[DEBUG AUTH] SambaError during login: {e}")
            flash(f"Authentication error: {e}", "danger")
    return render_template("login.html", form=form)


@auth_bp.route("/logout")
@login_required
def logout():
    from flask_login import current_user

    remove_session_user(current_user.id)
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for("auth.login"))
