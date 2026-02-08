"""User management routes."""

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import login_required

from app.forms import CreateUserForm, ResetPasswordForm, SetExpiryForm
from app.services.samba import (
    SambaError,
    create_user,
    delete_user,
    disable_user,
    enable_user,
    get_user,
    list_users,
    reset_password,
    set_user_expiry,
)

users_bp = Blueprint("users", __name__)


@users_bp.route("/")
@login_required
def index():
    try:
        usernames = list_users()
    except SambaError as e:
        flash(f"Error listing users: {e}", "danger")
        usernames = []
    return render_template("users/index.html", usernames=usernames)


@users_bp.route("/<username>")
@login_required
def detail(username):
    try:
        user_info = get_user(username)
    except SambaError as e:
        flash(f"Error loading user: {e}", "danger")
        return redirect(url_for("users.index"))
    password_form = ResetPasswordForm()
    expiry_form = SetExpiryForm()
    return render_template(
        "users/detail.html",
        username=username,
        user_info=user_info,
        password_form=password_form,
        expiry_form=expiry_form,
    )


@users_bp.route("/create", methods=["GET", "POST"])
@login_required
def create():
    form = CreateUserForm()
    if form.validate_on_submit():
        try:
            create_user(
                username=form.username.data,
                password=form.password.data,
                given_name=form.given_name.data or None,
                surname=form.surname.data or None,
                mail=form.mail.data or None,
                must_change_at_next_login=form.must_change_password.data,
            )
            flash(f"User '{form.username.data}' created successfully.", "success")
            return redirect(url_for("users.index"))
        except SambaError as e:
            flash(f"Error creating user: {e}", "danger")
    return render_template("users/create.html", form=form)


@users_bp.route("/<username>/delete", methods=["POST"])
@login_required
def remove(username):
    try:
        delete_user(username)
        flash(f"User '{username}' deleted.", "success")
    except SambaError as e:
        flash(f"Error deleting user: {e}", "danger")
    return redirect(url_for("users.index"))


@users_bp.route("/<username>/disable", methods=["POST"])
@login_required
def disable(username):
    try:
        disable_user(username)
        flash(f"User '{username}' disabled.", "success")
    except SambaError as e:
        flash(f"Error disabling user: {e}", "danger")
    return redirect(url_for("users.detail", username=username))


@users_bp.route("/<username>/enable", methods=["POST"])
@login_required
def enable(username):
    try:
        enable_user(username)
        flash(f"User '{username}' enabled.", "success")
    except SambaError as e:
        flash(f"Error enabling user: {e}", "danger")
    return redirect(url_for("users.detail", username=username))


@users_bp.route("/<username>/reset-password", methods=["POST"])
@login_required
def reset_pwd(username):
    form = ResetPasswordForm()
    if form.validate_on_submit():
        try:
            reset_password(username, form.new_password.data)
            flash(f"Password reset for '{username}'.", "success")
        except SambaError as e:
            flash(f"Error resetting password: {e}", "danger")
    else:
        for field, errs in form.errors.items():
            for err in errs:
                flash(f"{field}: {err}", "danger")
    return redirect(url_for("users.detail", username=username))


@users_bp.route("/<username>/set-expiry", methods=["POST"])
@login_required
def expiry(username):
    form = SetExpiryForm()
    if form.validate_on_submit():
        try:
            set_user_expiry(
                username,
                days=form.days.data if not form.no_expiry.data else None,
                no_expiry=form.no_expiry.data,
            )
            flash(f"Expiry updated for '{username}'.", "success")
        except SambaError as e:
            flash(f"Error setting expiry: {e}", "danger")
    return redirect(url_for("users.detail", username=username))
