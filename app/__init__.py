from flask import Flask
from config import Config
from app.game import bp as game_bp
from . import db
from datetime import timedelta

def create_app(config_class=Config): 
    app = Flask(__name__)
    app.config.from_object(config_class)
    app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=32)

    app.register_blueprint(game_bp)
    db.init_app(app)

    return app