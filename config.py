import os
from app.instance.config import SECRET_KEY

basedir = os.path.abspath(os.path.dirname(__file__))

class Config: 
    SECRET_KEY = SECRET_KEY
    BASEDIR = os.path.abspath(os.path.dirname(__file__))
    DATABASE = os.path.join(BASEDIR, 'app', 'instance', 'game.sqlite')
