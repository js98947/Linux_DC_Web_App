"""Basic tests for application startup and routing."""

import pytest

from app import create_app


@pytest.fixture
def app():
    app = create_app("development")
    app.config["WTF_CSRF_ENABLED"] = False
    app.config["TESTING"] = True
    return app


@pytest.fixture
def client(app):
    return app.test_client()


def test_app_creates(app):
    assert app is not None


def test_login_page_loads(client):
    response = client.get("/login")
    assert response.status_code == 200
    assert b"Sign In" in response.data or b"sign in" in response.data.lower()


def test_unauthenticated_redirect(client):
    """Unauthenticated users should be redirected to login."""
    response = client.get("/")
    assert response.status_code == 302
    assert "/login" in response.headers["Location"]


def test_users_page_requires_auth(client):
    response = client.get("/users/")
    assert response.status_code == 302


def test_groups_page_requires_auth(client):
    response = client.get("/groups/")
    assert response.status_code == 302


def test_computers_page_requires_auth(client):
    response = client.get("/computers/")
    assert response.status_code == 302
