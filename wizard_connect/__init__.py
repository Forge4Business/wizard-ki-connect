import os

from flask import Flask

from .auth import configure_keycloak, current_user
from .config import Config
from .extensions import csrf, db, oauth
from .routes import web
from .seed import seed_test_data


def create_app(test_config: dict | None = None) -> Flask:
    app = Flask(__name__, template_folder="../templates")
    os.makedirs(app.instance_path, exist_ok=True)
    app.config.from_object(Config)
    if test_config:
        app.config.update(test_config)
    else:
        Config.validate()
    db.init_app(app)
    csrf.init_app(app)
    oauth.init_app(app)
    configure_keycloak(app)
    app.register_blueprint(web)

    @app.context_processor
    def inject_globals():
        return {"current_user": current_user()}

    @app.after_request
    def security_headers(response):
        response.headers.setdefault("X-Content-Type-Options", "nosniff")
        response.headers.setdefault("X-Frame-Options", "SAMEORIGIN")
        response.headers.setdefault("Referrer-Policy", "strict-origin-when-cross-origin")
        response.headers.setdefault(
            "Content-Security-Policy",
            "default-src 'self'; style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net "
            "https://fonts.googleapis.com; font-src https://fonts.gstatic.com; "
            "script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
            "img-src 'self' data: https://ui-avatars.com https://img.icons8.com",
        )
        return response

    with app.app_context():
        db.create_all()
        if app.config["ENABLE_TEST_USERS"]:
            seed_test_data()
    return app
