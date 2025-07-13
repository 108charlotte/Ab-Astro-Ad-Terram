import os

basedir = os.path.abspath(os.path.dirname(__file__))

class Config: 
    SECRET_KEY = os.environ.get('SECRET_KEY')
    BASEDIR = os.path.abspath(os.path.dirname(__file__))
    DATABASE = os.path.join(BASEDIR, 'app', 'instance', 'game.sqlite')
