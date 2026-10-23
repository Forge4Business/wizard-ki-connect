from wizard_connect.extensions import db
from wizard_connect.models import Post, User
from wizard_connect.routes import validate_image_data


def test_public_pages_and_health(client):
    assert client.get("/").status_code == 200
    assert client.get("/login").status_code == 200
    assert client.get("/register").status_code == 200
    assert client.get("/healthz").get_json() == {"status": "ok"}


def test_test_users_are_hashed(app):
    with app.app_context():
        user = User.query.filter_by(username="irsan").one()
        assert user.password_hash != "admin123"
        assert user.check_password("admin123")


def test_login_rejects_wrong_password(client):
    response = client.post(
        "/login", data={"username": "irsan", "password": "wrong"}, follow_redirects=True
    )
    assert response.status_code == 200
    assert "Falscher Benutzername" in response.text


def test_dashboard_requires_login(client):
    response = client.get("/dashboard")
    assert response.status_code == 302
    assert response.headers["Location"].endswith("/login")


def test_csrf_blocks_untrusted_post(app, client):
    app.config["WTF_CSRF_ENABLED"] = True
    response = client.post("/login", data={"username": "irsan", "password": "admin123"})
    assert response.status_code == 400


def test_create_post_persists_and_adds_points(app, logged_in_client):
    response = logged_in_client.post(
        "/posts",
        data={"title": "Sicherer Test", "category": "Code", "content": "Bleibt erhalten."},
    )
    assert response.status_code == 302
    with app.app_context():
        assert Post.query.filter_by(title="Sicherer Test").one().content == "Bleibt erhalten."
        assert User.query.filter_by(username="irsan").one().score == 80


def test_post_content_is_escaped(logged_in_client):
    logged_in_client.post(
        "/posts",
        data={"title": "XSS", "category": "General", "content": "<script>alert(1)</script>"},
    )
    response = logged_in_client.get("/dashboard")
    assert "&lt;script&gt;alert(1)&lt;/script&gt;" in response.text
    assert "<script>alert(1)</script>" not in response.text


def test_image_validation_rejects_html_payload():
    try:
        validate_image_data('data:image/svg+xml,<svg onload="alert(1)">')
    except ValueError:
        pass
    else:
        raise AssertionError("Unsichere Bilddaten wurden akzeptiert")


def test_registration_creates_hashed_password(app, client):
    response = client.post(
        "/register",
        data={"username": "newuser", "email": "new@example.com", "password": "very-secure"},
    )
    assert response.status_code == 302
    with app.app_context():
        user = db.session.scalar(db.select(User).filter_by(username="newuser"))
        assert user and user.check_password("very-secure")
