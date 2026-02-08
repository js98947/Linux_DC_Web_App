"""Unit tests for the samba service layer (mocked)."""

import subprocess
from unittest.mock import patch, MagicMock

import pytest

from app import create_app


@pytest.fixture
def app():
    app = create_app("development")
    app.config["TESTING"] = True
    return app


@pytest.fixture
def app_ctx(app):
    with app.app_context():
        yield app


def test_parse_ldif_output(app_ctx):
    from app.services.samba import _parse_ldif_output

    output = """dn: CN=testuser,CN=Users,DC=example,DC=local
cn: testuser
sAMAccountName: testuser
userPrincipalName: testuser@example.local
objectClass: top
objectClass: person
objectClass: user"""

    result = _parse_ldif_output(output)
    assert result["cn"] == "testuser"
    assert result["sAMAccountName"] == "testuser"
    # objectClass appears multiple times, should be a list
    assert isinstance(result["objectClass"], list)
    assert "user" in result["objectClass"]


@patch("app.services.samba.subprocess.run")
def test_list_users(mock_run, app_ctx):
    from app.services.samba import list_users

    mock_run.return_value = MagicMock(
        returncode=0,
        stdout="Administrator\nkrbtgt\ntestuser\n",
        stderr="",
    )
    users = list_users()
    assert "Administrator" in users
    assert "testuser" in users
    assert len(users) == 3


@patch("app.services.samba.subprocess.run")
def test_list_users_error(mock_run, app_ctx):
    from app.services.samba import list_users, SambaError

    mock_run.return_value = MagicMock(
        returncode=1,
        stdout="",
        stderr="ERROR: something went wrong",
    )
    with pytest.raises(SambaError):
        list_users()


@patch("app.services.samba.subprocess.run")
def test_create_user(mock_run, app_ctx):
    from app.services.samba import create_user

    mock_run.return_value = MagicMock(
        returncode=0,
        stdout="User 'newuser' created successfully\n",
        stderr="",
    )
    result = create_user("newuser", "P@ssw0rd123", given_name="New", surname="User")
    assert "created" in result.lower() or "newuser" in result.lower()

    call_args = mock_run.call_args[0][0]
    assert "user" in call_args
    assert "create" in call_args
    assert "newuser" in call_args
    assert "--given-name" in call_args
    assert "--surname" in call_args
