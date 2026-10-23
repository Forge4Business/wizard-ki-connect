import base64
import binascii
import re

from flask import Blueprint, current_app, flash, redirect, render_template, request, session, url_for
from sqlalchemy import desc

from .auth import current_user, login_required, upsert_keycloak_user
from .extensions import db, oauth
from .models import Post, User


web = Blueprint("web", __name__)
ALLOWED_CATEGORIES = {"General", "Code", "Fail"}
IMAGE_RE = re.compile(r"^data:image/(png|jpeg|gif|webp);base64,([A-Za-z0-9+/=]+)$")
MAX_IMAGE_BYTES = 2 * 1024 * 1024


def validate_image_data(value: str) -> str | None:
    if not value:
        return None
    match = IMAGE_RE.fullmatch(value)
    if not match:
        raise ValueError("Das Bildformat wird nicht unterstützt.")
    try:
        raw = base64.b64decode(match.group(2), validate=True)
    except (binascii.Error, ValueError) as exc:
        raise ValueError("Die Bilddaten sind ungültig.") from exc
    if len(raw) > MAX_IMAGE_BYTES:
        raise ValueError("Das Bild darf höchstens 2 MB groß sein.")
    return value


@web.get("/")
def index():
    if current_user():
        return redirect(url_for("web.dashboard"))
    return render_template("index.html")


@web.get("/healthz")
def health():
    db.session.execute(db.select(User.id).limit(1))
    return {"status": "ok"}


@web.route("/login", methods=["GET", "POST"])
def login():
    if current_user():
        return redirect(url_for("web.dashboard"))
    if current_app.config["AUTH_MODE"] == "keycloak":
        return redirect(url_for("web.keycloak_login"))
    if request.method == "POST":
        username = request.form.get("username", "").strip().lower()
        password = request.form.get("password", "")
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            session.clear()
            session["user_id"] = user.id
            return redirect(url_for("web.dashboard"))
        flash("Falscher Benutzername oder Passwort.", "danger")
    return render_template("login.html")


@web.route("/register", methods=["GET", "POST"])
def register():
    if current_app.config["AUTH_MODE"] != "local":
        return redirect(url_for("web.login"))
    if request.method == "POST":
        username = request.form.get("username", "").strip().lower()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        if len(username) < 3 or len(password) < 10 or "@" not in email:
            flash("Bitte gültige Daten und ein Passwort mit mindestens 10 Zeichen angeben.", "danger")
        elif User.query.filter((User.username == username) | (User.email == email)).first():
            flash("Benutzername oder E-Mail ist bereits vergeben.", "danger")
        else:
            user = User(username=username, name=username, email=email, role="user")
            user.set_password(password)
            db.session.add(user)
            db.session.commit()
            flash("Account erstellt. Du kannst dich jetzt anmelden.", "success")
            return redirect(url_for("web.login"))
    return render_template("register.html")


@web.get("/auth/keycloak")
def keycloak_login():
    if current_app.config["AUTH_MODE"] != "keycloak":
        return redirect(url_for("web.login"))
    redirect_uri = url_for("web.keycloak_callback", _external=True, _scheme="https")
    return oauth.keycloak.authorize_redirect(redirect_uri)


@web.get("/auth/callback")
def keycloak_callback():
    if current_app.config["AUTH_MODE"] != "keycloak":
        return redirect(url_for("web.login"))
    token = oauth.keycloak.authorize_access_token()
    claims = token.get("userinfo") or oauth.keycloak.userinfo(token=token)
    user = upsert_keycloak_user(claims)
    session.clear()
    session["user_id"] = user.id
    return redirect(url_for("web.dashboard"))


@web.post("/logout")
def logout():
    session.clear()
    return redirect(url_for("web.index"))


@web.get("/dashboard")
@login_required
def dashboard():
    user = current_user()
    posts = Post.query.order_by(desc(Post.created_at)).all()
    leaderboard = User.query.order_by(desc(User.score), User.name).limit(10).all()
    return render_template(
        "dashboard.html",
        user=user,
        posts=posts,
        leaderboard=leaderboard,
        channel_url=current_app.config["OPENWEBUI_CHANNEL_URL"],
    )


@web.post("/posts")
@login_required
def create_post():
    title = request.form.get("title", "").strip()
    content = request.form.get("content", "").strip()
    category = request.form.get("category", "General")
    if not title or not content or len(title) > 160 or category not in ALLOWED_CATEGORIES:
        flash("Bitte Titel, Kategorie und Beschreibung korrekt ausfüllen.", "danger")
        return redirect(url_for("web.dashboard"))
    try:
        image_data = validate_image_data(request.form.get("image_data", ""))
    except ValueError as exc:
        flash(str(exc), "danger")
        return redirect(url_for("web.dashboard"))
    user = current_user()
    db.session.add(
        Post(title=title, category=category, content=content, image_data=image_data, author=user)
    )
    user.score += 10
    db.session.commit()
    flash("Beitrag erfolgreich gespeichert. (+10 Punkte)", "success")
    return redirect(url_for("web.dashboard"))
