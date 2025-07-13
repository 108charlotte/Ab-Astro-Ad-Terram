from flask import render_template, session
from app.game import bp
from app.db import get_db

@bp.before_app_request
def make_session_permanent(): 
    session.permanent = True

@bp.before_app_request
def check_player_id_exists():
    db = get_db()
    player_id = session.get('player_id')

    if not player_id:
        cur = db.execute('INSERT INTO players (nickname, current_location_id) VALUES (?, ?)', ('Guest', 0))
        db.commit()
        session['player_id'] = cur.lastrowid
        print(f"Created new player with id {cur.lastrowid}")
    else:
        cur = db.execute('SELECT * FROM players WHERE player_id = ?', (player_id,))
        player = cur.fetchone()

        if player is None:
            session.pop('player_id')
            print(f"No player found with id {player_id}. Resetting session player_id.")
        else:
            if player['current_location_id'] is None:
                db.execute('UPDATE players SET current_location_id = ? WHERE player_id = ?', (0, player_id))
                db.commit()
                print(f"Assigned default location (0) to player {player_id}")

@bp.route('/')
def index(): 
    db = get_db()
    player_id = session.get('player_id')
    quests = [""]
    story_log = [""]
    location = ""
    if player_id: 
        # cur = db.execute('SELECT * FROM quest_log WHERE player_id = ?', (player_id,))
        cur = db.execute('SELECT * FROM quest_definitions')
        quests = cur.fetchall()
        cur = db.execute('SELECT * FROM story_log WHERE player_id = ?', (player_id,))
        story_log = cur.fetchall()
        cur = db.execute('SELECT * FROM players WHERE player_id = ?', (player_id,))
        player = cur.fetchone()
        location_id = player['current_location_id']
        cur = db.execute('SELECT * FROM locations WHERE location_id = ?', (location_id,))
        location = cur.fetchone()
        location = location['location_name']
    return render_template('index.html', quests=quests, story_log=story_log, location=location)