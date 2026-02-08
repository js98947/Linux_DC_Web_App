"""Group management routes."""

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import login_required

from app.forms import CreateGroupForm, GroupMemberForm
from app.services.samba import (
    SambaError,
    add_group_members,
    create_group,
    delete_group,
    get_group,
    list_group_members,
    list_groups,
    remove_group_members,
)

groups_bp = Blueprint("groups", __name__)


@groups_bp.route("/")
@login_required
def index():
    try:
        groupnames = list_groups()
    except SambaError as e:
        flash(f"Error listing groups: {e}", "danger")
        groupnames = []
    return render_template("groups/index.html", groupnames=groupnames)


@groups_bp.route("/<groupname>")
@login_required
def detail(groupname):
    try:
        group_info = get_group(groupname)
    except SambaError as e:
        flash(f"Error loading group: {e}", "danger")
        return redirect(url_for("groups.index"))

    try:
        members = list_group_members(groupname)
    except SambaError:
        members = []

    add_form = GroupMemberForm(prefix="add")
    remove_form = GroupMemberForm(prefix="remove")
    return render_template(
        "groups/detail.html",
        groupname=groupname,
        group_info=group_info,
        members=members,
        add_form=add_form,
        remove_form=remove_form,
    )


@groups_bp.route("/create", methods=["GET", "POST"])
@login_required
def create():
    form = CreateGroupForm()
    if form.validate_on_submit():
        try:
            create_group(
                groupname=form.groupname.data,
                description=form.description.data or None,
                group_type=form.group_type.data,
            )
            flash(f"Group '{form.groupname.data}' created.", "success")
            return redirect(url_for("groups.index"))
        except SambaError as e:
            flash(f"Error creating group: {e}", "danger")
    return render_template("groups/create.html", form=form)


@groups_bp.route("/<groupname>/delete", methods=["POST"])
@login_required
def remove(groupname):
    try:
        delete_group(groupname)
        flash(f"Group '{groupname}' deleted.", "success")
    except SambaError as e:
        flash(f"Error deleting group: {e}", "danger")
    return redirect(url_for("groups.index"))


@groups_bp.route("/<groupname>/add-members", methods=["POST"])
@login_required
def add_members(groupname):
    form = GroupMemberForm(prefix="add")
    if form.validate_on_submit():
        try:
            add_group_members(groupname, form.members.data)
            flash(f"Members added to '{groupname}'.", "success")
        except SambaError as e:
            flash(f"Error adding members: {e}", "danger")
    return redirect(url_for("groups.detail", groupname=groupname))


@groups_bp.route("/<groupname>/remove-members", methods=["POST"])
@login_required
def rem_members(groupname):
    form = GroupMemberForm(prefix="remove")
    if form.validate_on_submit():
        try:
            remove_group_members(groupname, form.members.data)
            flash(f"Members removed from '{groupname}'.", "success")
        except SambaError as e:
            flash(f"Error removing members: {e}", "danger")
    return redirect(url_for("groups.detail", groupname=groupname))
