import os
from app.instance.config import SECRET_KEY

basedir = os.path.abspath(os.path.dirname(__file__))

class Config: 
    SECRET_KEY = os.environ.get('SECRET_KEY') or SECRET_KEY
    BASEDIR = os.path.abspath(os.path.dirname(__file__))
    
    if os.environ.get('DATABASE_URL'):
        DATABASE = os.environ.get('DATABASE_URL')
    else:
        DATABASE = os.path.join(BASEDIR, 'app', 'instance', 'game.sqlite')
