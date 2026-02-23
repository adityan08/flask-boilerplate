import logging
import redis

from flask import Flask
from flasgger import Swagger
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_migrate import Migrate
from flask_compress import Compress
from flask_marshmallow import Marshmallow
from logging.handlers import RotatingFileHandler

from app.core.config import Config_is

db = SQLAlchemy()
migrate = Migrate()
redis_obj = redis.StrictRedis.from_url(Config_is.REDIS_URL, decode_responses=True)
app = None


def create_app(config_class=Config_is):
    global app
    if app:
        return app
    
    app = Flask(__name__, template_folder='templates')
    app.config.from_object(config_class)
    app.config['SQLALCHEMY_POOL_RECYCLE'] = 1200
    app.config['SQLALCHEMY_POOL_PRE_PING'] = True

    db.init_app(app)
    compress = Compress()
    migrate.init_app(app, db)
    Marshmallow(app)
    CORS(app)
    compress.init_app(app)
    
    swagger_config = {
        "headers": [],
        "specs": [
            {
                "endpoint": 'apispec',
                "route": '/apispec.json',
                "rule_filter": lambda rule: True,
                "model_filter": lambda tag: True,
            }
        ],
        "static_url_path": "/flasgger_static",
        "swagger_ui": True,
        "specs_route": "/docs/"
    }

    swagger_template = {
        "info": {
            "title": "My API",
            "description": "API Documentation",
            "version": "1.0.0"
        }
    }
    Swagger(app, config=swagger_config, template=swagger_template)
    
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler = RotatingFileHandler('log_data.log', maxBytes=1000000, backupCount=5)
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)

    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    root_logger.handlers.clear()
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)

    # Prevent Flask's app.logger from double-logging
    app.logger.handlers.clear()
    app.logger.propagate = True

    @app.teardown_appcontext
    def shutdown_session(exception=None):
        db.session.remove()

    from app.api import bp as api_bp
    app.register_blueprint(api_bp)

    with app.app_context():
        from app import models

    return app
