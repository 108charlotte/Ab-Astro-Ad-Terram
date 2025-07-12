from flask import render_template
from app.main import bp
from app.game import Game

game = Game()

@bp.route('/')
def index(): 
    return render_template('index.html')