"""WTForms form definitions."""

from flask_wtf import FlaskForm
from wtforms import (
    BooleanField,
    IntegerField,
    PasswordField,
    SelectField,
    StringField,
    SubmitField,
    TextAreaField,
)
from wtforms.validators import DataRequired, Email, EqualTo, Length, Optional


class LoginForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Sign In")


class CreateUserForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired(), Length(min=1, max=64)])
    password = PasswordField("Password", validators=[DataRequired(), Length(min=8)])
    confirm_password = PasswordField(
        "Confirm Password", validators=[DataRequired(), EqualTo("password")]
    )
    given_name = StringField("First Name", validators=[Optional(), Length(max=64)])
    surname = StringField("Last Name", validators=[Optional(), Length(max=64)])
    mail = StringField("Email", validators=[Optional(), Email()])
    must_change_password = BooleanField("Must change password at next login")
    submit = SubmitField("Create User")


class ResetPasswordForm(FlaskForm):
    new_password = PasswordField("New Password", validators=[DataRequired(), Length(min=8)])
    confirm_password = PasswordField(
        "Confirm Password", validators=[DataRequired(), EqualTo("new_password")]
    )
    submit = SubmitField("Reset Password")


class SetExpiryForm(FlaskForm):
    no_expiry = BooleanField("Never expires")
    days = IntegerField("Expires in (days)", validators=[Optional()])
    submit = SubmitField("Set Expiry")


class CreateGroupForm(FlaskForm):
    groupname = StringField("Group Name", validators=[DataRequired(), Length(min=1, max=64)])
    description = StringField("Description", validators=[Optional(), Length(max=256)])
    group_type = SelectField(
        "Group Type",
        choices=[("Security", "Security"), ("Distribution", "Distribution")],
        default="Security",
    )
    submit = SubmitField("Create Group")


class GroupMemberForm(FlaskForm):
    members = StringField(
        "Members",
        validators=[DataRequired()],
        description="Comma-separated list of usernames",
    )
    submit = SubmitField("Update Members")


class CreateComputerForm(FlaskForm):
    computer_name = StringField(
        "Computer Name", validators=[DataRequired(), Length(min=1, max=64)]
    )
    description = StringField("Description", validators=[Optional(), Length(max=256)])
    ip_address = StringField("IP Address", validators=[Optional()])
    submit = SubmitField("Add Computer")
