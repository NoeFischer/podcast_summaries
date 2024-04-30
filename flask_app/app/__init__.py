from flask import Flask
from app.config import ProdConfig


def create_app(config_object: callable = ProdConfig) -> Flask:
    app = Flask(__name__)
    app.config.from_object(config_object)

    # Registering Blueprints
    from app.views import main as main_blueprint

    app.register_blueprint(main_blueprint)

    return app
