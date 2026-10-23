import os
import secrets
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent


def _as_bool(value: str | None, default: bool = False) -> bool:
    if value is None:
        return default
    return value.lower() in {"1", "true", "yes", "on"}


class Config:
    ENVIRONMENT = os.getenv("APP_ENV", "development")
    AUTH_MODE = os.getenv("AUTH_MODE", "local").lower()
    SECRET_KEY = os.getenv("SECRET_KEY") or secrets.token_hex(32)
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL", f"sqlite:///{BASE_DIR / 'instance' / 'wizard_connect.db'}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MAX_CONTENT_LENGTH = 3 * 1024 * 1024
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    SESSION_COOKIE_SECURE = ENVIRONMENT == "production"
    WTF_CSRF_TIME_LIMIT = 3600
    ENABLE_TEST_USERS = _as_bool(
        os.getenv("ENABLE_TEST_USERS"), default=ENVIRONMENT != "production"
    )
    OPENWEBUI_CHANNEL_URL = os.getenv(
        "OPENWEBUI_CHANNEL_URL",
        "https://ki.wizard.de/channels/cd0c970a-1ee5-4f4c-bfde-f89dfe2711a9",
    )
    KEYCLOAK_SERVER_URL = os.getenv("KEYCLOAK_SERVER_URL", "").rstrip("/")
    KEYCLOAK_REALM = os.getenv("KEYCLOAK_REALM", "")
    KEYCLOAK_CLIENT_ID = os.getenv("KEYCLOAK_CLIENT_ID", "")
    KEYCLOAK_CLIENT_SECRET = os.getenv("KEYCLOAK_CLIENT_SECRET", "")
    KEYCLOAK_ADMIN_ROLE = os.getenv("KEYCLOAK_ADMIN_ROLE", "wizard-admin")

    @classmethod
    def validate(cls) -> None:
        if cls.ENVIRONMENT == "production" and not os.getenv("SECRET_KEY"):
            raise RuntimeError("SECRET_KEY muss in Produktion gesetzt sein.")
        if cls.AUTH_MODE not in {"local", "keycloak"}:
            raise RuntimeError("AUTH_MODE muss 'local' oder 'keycloak' sein.")
        if cls.AUTH_MODE == "keycloak":
            required = {
                "KEYCLOAK_SERVER_URL": cls.KEYCLOAK_SERVER_URL,
                "KEYCLOAK_REALM": cls.KEYCLOAK_REALM,
                "KEYCLOAK_CLIENT_ID": cls.KEYCLOAK_CLIENT_ID,
                "KEYCLOAK_CLIENT_SECRET": cls.KEYCLOAK_CLIENT_SECRET,
            }
            missing = [name for name, value in required.items() if not value]
            if missing:
                raise RuntimeError(f"Fehlende Keycloak-Konfiguration: {', '.join(missing)}")
