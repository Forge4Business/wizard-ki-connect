import pytest

from wizard_connect import create_app
from wizard_connect.extensions import db


@pytest.fixture()
def app():
    app = create_app(
        {
            "TESTING": True,
            "SECRET_KEY": "test-secret",
            "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
            "WTF_CSRF_ENABLED": False,
            "ENABLE_TEST_USERS": True,
            "AUTH_MODE": "local",
        }
    )
    yield app
    with app.app_context():
        db.drop_all()


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def logged_in_client(client):
    response = client.post("/login", data={"username": "irsan", "password": "admin123"})
    assert response.status_code == 302
    return client
