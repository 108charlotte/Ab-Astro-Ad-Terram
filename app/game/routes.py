from flask import render_template, session
from app.game import bp
from app.db import get_db

@bp.before_app_request
def check_player_id_exists(): 
    if 'player_id' not in session: 
        db = get_db()
        cur = db.execute('INSERT INTO players (nickname) VALUES (?)', ('Guest',))
        db.commit()
        session['player_id'] = cur.lastrowid

@bp.route('/')
def index(): 
    db = get_db()
    player_id = session.get('player_id')
    quests = [""]
    story_log = [""]
    if player_id: 
        # cur = db.execute('SELECT * FROM quest_log WHERE player_id = ?', (player_id,))
        cur = db.execute('SELECT * FROM quest_definitions')
        quests = cur.fetchall()
        cur = db.execute('SELECT * FROM story_log WHERE player_id = ?', (player_id,))
        story_log = cur.fetchall()
    return render_template('index.html', quests=quests, story_log=story_log)