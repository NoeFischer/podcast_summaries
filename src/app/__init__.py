from flask import Flask
import os
from app.config import DevConfig, ProdConfig


def create_app():
    app = Flask(__name__)

    # Configuration
    if os.getenv("FLASK_ENV") == "development":
        app.config.from_object(DevConfig)
    else:
        app.config.from_object(ProdConfig)

    # Registering Blueprints
    from app.views import main as main_blueprint

    app.register_blueprint(main_blueprint)

    return app
