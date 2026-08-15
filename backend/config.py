import os
from datetime import timedelta

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from sqlalchemy import MetaData

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

# Error monitoring - only activates if SENTRY_DSN is set (get one free at
# sentry.io). Wrapped in a try/except so a bad DSN or network hiccup at
# startup never prevents the app itself from booting.
sentry_dsn = os.environ.get("SENTRY_DSN")
if sentry_dsn:
    try:
        import sentry_sdk
        from sentry_sdk.integrations.flask import FlaskIntegration

        sentry_sdk.init(
            dsn=sentry_dsn,
            integrations=[FlaskIntegration()],
            traces_sample_rate=0.1,
            environment=os.environ.get("SENTRY_ENVIRONMENT", "production"),
        )
    except Exception as err:
        print(f"[sentry] Could not initialize: {err}")

convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}
metadata = MetaData(naming_convention=convention)

app = Flask(__name__)

db_url = os.environ.get("DATABASE_URL", f"sqlite:///{os.path.join(BASE_DIR, 'instance', 'app.db')}")
# Render/Heroku-style Postgres URLs start with postgres://, SQLAlchemy needs postgresql://
if db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql://", 1)

app.config["SQLALCHEMY_DATABASE_URI"] = db_url
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["JWT_SECRET_KEY"] = os.environ.get("JWT_SECRET_KEY", "dev-secret-change-me")
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(days=30)
app.json.compact = False

db = SQLAlchemy(metadata=metadata)
db.init_app(app)
migrate = Migrate(app, db)
jwt = JWTManager(app)

# In-memory storage is fine here: Render's free/starter plan runs a single
# worker process (WEB_CONCURRENCY=1 in render.yaml), so there's only ever
# one counter to keep in sync. If you scale to multiple workers/instances
# later, swap storage_uri to a shared Redis instance instead.
limiter = Limiter(
    key_func=get_remote_address,
    app=app,
    default_limits=[],
    storage_uri="memory://",
)

CORS(
    app,
    resources={r"/*": {"origins": os.environ.get("FRONTEND_ORIGIN", "*")}},
    supports_credentials=True,
)