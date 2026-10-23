from functools import wraps

from flask import current_app, flash, redirect, session, url_for

from .extensions import db, oauth
from .models import User


def current_user() -> User | None:
    user_id = session.get("user_id")
    return db.session.get(User, user_id) if user_id else None


def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if current_user() is None:
            flash("Bitte zuerst anmelden.", "warning")
            return redirect(url_for("web.login"))
        return view(*args, **kwargs)

    return wrapped


def configure_keycloak(app) -> None:
    if app.config["AUTH_MODE"] != "keycloak":
        return
    metadata_url = (
        f"{app.config['KEYCLOAK_SERVER_URL']}/realms/"
        f"{app.config['KEYCLOAK_REALM']}/.well-known/openid-configuration"
    )
    oauth.register(
        name="keycloak",
        client_id=app.config["KEYCLOAK_CLIENT_ID"],
        client_secret=app.config["KEYCLOAK_CLIENT_SECRET"],
        server_metadata_url=metadata_url,
        client_kwargs={"scope": "openid profile email"},
    )


def upsert_keycloak_user(claims: dict) -> User:
    subject = claims["sub"]
    user = User.query.filter_by(keycloak_subject=subject).first()
    if user is None and claims.get("email"):
        user = User.query.filter_by(email=claims["email"]).first()
    if user is None:
        user = User(
            username=claims.get("preferred_username", subject),
            email=claims.get("email", f"{subject}@keycloak.local"),
            name=claims.get("name") or claims.get("preferred_username", subject),
        )
    roles = claims.get("realm_access", {}).get("roles", [])
    user.keycloak_subject = subject
    user.username = claims.get("preferred_username", user.username)
    user.name = claims.get("name", user.name)
    user.role = "admin" if current_app.config["KEYCLOAK_ADMIN_ROLE"] in roles else "user"
    db.session.add(user)
    db.session.commit()
    return user
