"""Dashboard / home page."""

from flask import Blueprint, render_template
from flask_login import login_required

from app.services.samba import (
    SambaError,
    domain_level,
    list_computers,
    list_groups,
    list_users,
)

dashboard_bp = Blueprint("dashboard", __name__)


@dashboard_bp.route("/")
@login_required
def index():
    stats = {}
    errors = []
    try:
        stats["user_count"] = len(list_users())
    except SambaError as e:
        stats["user_count"] = "?"
        errors.append(f"Users: {e}")

    try:
        stats["group_count"] = len(list_groups())
    except SambaError as e:
        stats["group_count"] = "?"
        errors.append(f"Groups: {e}")

    try:
        stats["computer_count"] = len(list_computers())
    except SambaError as e:
        stats["computer_count"] = "?"
        errors.append(f"Computers: {e}")

    try:
        stats["domain_level"] = domain_level().strip()
    except SambaError:
        stats["domain_level"] = "Unavailable"

    return render_template("dashboard.html", stats=stats, errors=errors)
