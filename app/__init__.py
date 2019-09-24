import logging

from config import Config
from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()
migrate = Migrate()


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    migrate.init_app(app, db)

    from app.request_logger import log_request, log_response

    @app.before_request
    def before_request():
        log_request(app.logger)

    @app.after_request
    def after_request(response):
        return log_response(response, app.logger)

    from app.main import bp as main_bp

    app.register_blueprint(main_bp)

    from app.api import bp as api_bp

    app.register_blueprint(api_bp, url_prefix="/api")

    if not app.testing:
        werkzeug_log = logging.getLogger("werkzeug")
        werkzeug_log.setLevel(logging.ERROR)

        formatter = logging.Formatter(
            "[%(asctime)s] %(name)s %(levelname)s %(message)s"
        )
        for handler in app.logger.handlers:
            if type(handler) == logging.StreamHandler:
                handler.setFormatter(formatter)
                handler.setLevel(logging.DEBUG)
        app.logger.setLevel(logging.DEBUG)
        app.logger.info("Walter startup")
    return app


from app import models
