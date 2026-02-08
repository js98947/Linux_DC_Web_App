"""User model for Flask-Login session management.

Users are authenticated against Samba AD. This model is an in-memory
representation used only for the Flask session — no local database needed.
"""

from flask_login import UserMixin

from app import login_manager


class User(UserMixin):
    def __init__(self, username):
        self.id = username
        self.username = username


# In-memory session store — maps username -> User object for active sessions.
_active_users = {}


def get_or_create_session_user(username):
    if username not in _active_users:
        _active_users[username] = User(username)
    return _active_users[username]


def remove_session_user(username):
    _active_users.pop(username, None)


@login_manager.user_loader
def load_user(user_id):
    return _active_users.get(user_id)
