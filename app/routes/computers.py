"""Computer / machine account management routes."""

from flask import Blueprint, flash, redirect, render_template, url_for
from flask_login import login_required

from app.forms import CreateComputerForm
from app.services.samba import (
    SambaError,
    create_computer,
    delete_computer,
    get_computer,
    list_computers,
)

computers_bp = Blueprint("computers", __name__)


@computers_bp.route("/")
@login_required
def index():
    try:
        computer_names = list_computers()
    except SambaError as e:
        flash(f"Error listing computers: {e}", "danger")
        computer_names = []
    return render_template("computers/index.html", computer_names=computer_names)


@computers_bp.route("/<computer_name>")
@login_required
def detail(computer_name):
    try:
        computer_info = get_computer(computer_name)
    except SambaError as e:
        flash(f"Error loading computer: {e}", "danger")
        return redirect(url_for("computers.index"))
    return render_template(
        "computers/detail.html",
        computer_name=computer_name,
        computer_info=computer_info,
    )


@computers_bp.route("/create", methods=["GET", "POST"])
@login_required
def create():
    form = CreateComputerForm()
    if form.validate_on_submit():
        try:
            create_computer(
                computer_name=form.computer_name.data,
                description=form.description.data or None,
                ip_address=form.ip_address.data or None,
            )
            flash(f"Computer '{form.computer_name.data}' added.", "success")
            return redirect(url_for("computers.index"))
        except SambaError as e:
            flash(f"Error adding computer: {e}", "danger")
    return render_template("computers/create.html", form=form)


@computers_bp.route("/<computer_name>/delete", methods=["POST"])
@login_required
def remove(computer_name):
    try:
        delete_computer(computer_name)
        flash(f"Computer '{computer_name}' deleted.", "success")
    except SambaError as e:
        flash(f"Error deleting computer: {e}", "danger")
    return redirect(url_for("computers.index"))
