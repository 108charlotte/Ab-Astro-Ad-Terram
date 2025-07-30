import os

basedir = os.path.abspath(os.path.dirname(__file__))

class Config: 
    # Use environment variable or a fallback for development
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    BASEDIR = os.path.abspath(os.path.dirname(__file__))
    
    DATABASE = os.environ.get('DATABASE_URL', os.path.join(basedir, 'app', 'instance', 'game.sqlite'))
