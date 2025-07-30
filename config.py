import os
from app.instance.config import SECRET_KEY

basedir = os.path.abspath(os.path.dirname(__file__))

class Config: 
    SECRET_KEY = os.environ.get('SECRET_KEY') or SECRET_KEY
    BASEDIR = os.path.abspath(os.path.dirname(__file__))
    
    DATABASE = os.environ.get('DATABASE_URL', os.path.join(basedir, 'app', 'instance', 'game.sqlite'))
