from dotenv import load_dotenv
import os
load_dotenv()


def _clean(value):
    if value is None:
        return None
    value = str(value).strip().strip("'").strip('"')
    lowered = value.lower()
    if value == "" or lowered in {"none", "null"}:
        return None
    # Ignore template placeholders from .env.example
    if lowered.startswith("your-") or "your-" in lowered:
        return None
    return value


def _parse_int(value, default=None):
    value = _clean(value)
    if value is None:
        return default
    try:
        return int(value)
    except ValueError:
        return default


def _parse_bool(value, default=False):
    value = _clean(value)
    if value is None:
        return default
    return value.lower() in {"1", "true", "yes", "on"}


class Config:
    # Prefer DATABASE_URL when available.
    _database_url = _clean(os.getenv("DATABASE_URL"))
    _db_host = _clean(os.getenv("DB_HOST") or os.getenv("HOST"))
    _db_port = _parse_int(os.getenv("DB_PORT") or os.getenv("DATABASE_PORT") or os.getenv("PORT"), default=5432)
    _db_name = _clean(os.getenv("DB_NAME") or os.getenv("DATABASE"))
    _db_user = _clean(os.getenv("DB_USER") or os.getenv("USERNAME"))
    _db_password = _clean(os.getenv("DB_PASSWORD") or os.getenv("DATABASE_PASSWORD"))

    if _database_url:
        SQLALCHEMY_DATABASE_URI = _database_url
    elif all([_db_host, _db_name, _db_user]):
        db_auth = _db_user if _db_password is None else f"{_db_user}:{_db_password}"
        SQLALCHEMY_DATABASE_URI = f"postgresql+psycopg2://{db_auth}@{_db_host}:{_db_port}/{_db_name}"
    else:
        # Local/dev fallback when DB environment variables are not configured.
        SQLALCHEMY_DATABASE_URI = "sqlite:///aarogya_centre.db"

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Flask-Mail config with backward-compatible env keys.
    MAIL_SERVER = _clean(os.getenv("MAIL_SERVER") or os.getenv("SERVER"))
    MAIL_PORT = _parse_int(os.getenv("MAIL_PORT") or os.getenv("EMAIL_PORT"), default=587)
    MAIL_USERNAME = _clean(os.getenv("MAIL_USERNAME") or os.getenv("EMAIL"))
    MAIL_PASSWORD = _clean(os.getenv("MAIL_PASSWORD") or os.getenv("EMAIL_PASSWORD"))
    MAIL_USE_TLS = _parse_bool(os.getenv("MAIL_USE_TLS") or os.getenv("USE_TLS"), default=True)
    MAIL_USE_SSL = _parse_bool(os.getenv("MAIL_USE_SSL") or os.getenv("USE_SSL"), default=False)
