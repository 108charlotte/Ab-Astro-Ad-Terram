from flask import Flask
from config import Config
from app.game import bp as game_bp
from . import db

def create_app(config_class=Config): 
    app = Flask(__name__)
    app.config.from_object(config_class)

    app.register_blueprint(game_bp)
    db.init_app(app)

    return app