from datetime import datetime

from flask import Flask
from flask_bootstrap import Bootstrap
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

from config import Config

bootstrap = Bootstrap()
login = LoginManager()
db = SQLAlchemy()
migrate = Migrate()


def create_app(config_class: object = Config) -> Flask:
    # Create the Flask app
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize third-party applications
    bootstrap.init_app(app)
    login.init_app(app)
    db.init_app(app)
    migrate.init_app(app, db)

    # Timesince filter
    @app.template_filter("timesince")
    def timesince(dt: datetime, default: str = "just now") -> str:
        """
        Returns string representing "time since" e.g.
        3 days ago, 5 hours ago etc.
        """

        now = datetime.utcnow()
        diff = now - dt

        periods = ((diff.days / 365, "year", "years"),
                   (diff.days / 30, "month", "months"),
                   (diff.days / 7, "week", "weeks"), (diff.days, "day", "days"),
                   (diff.seconds / 3600, "hour", "hours"),
                   (diff.seconds / 60, "minute", "minutes"),
                   (diff.seconds, "second", "seconds"),)

        for period, singular, plural in periods:

            if period:
                return "%d %s ago" % (
                    period, singular if period == 1 else plural)

        return default

    # Import and inject all the necessary blueprints
    from forum.auth import auth_bp
    app.register_blueprint(auth_bp)

    from forum.main import main_bp
    app.register_blueprint(main_bp)

    from forum.board import board_bp
    app.register_blueprint(board_bp, url_prefix="/boards")

    from forum.thread import thread_bp
    app.register_blueprint(thread_bp,
                           url_prefix="/boards/<int:board_id>/threads")

    return app


from forum import models, filters
