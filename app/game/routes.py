from flask import render_template, session, redirect, request, url_for
from app.game import bp
from app.db import get_db
from .utils import initialize_new_player, process
import uuid

@bp.before_app_request
def make_session_permanent(): 
    session.permanent = True

@bp.before_app_request
def check_player_id_exists():

    if 'session_uuid' not in session: 
        session['session_uuid'] = str(uuid.uuid4())

    player_id = session.get('player_id')
    db = get_db()

    if not player_id:
        cur = db.execute('INSERT INTO players (current_location_id) VALUES (?)', (10, ))
        db.commit()
        session['player_id'] = cur.lastrowid
        print(f"Created new player with id {cur.lastrowid}")
        initialize_new_player(db, session.get('player_id'))
    else:
        cur = db.execute('SELECT * FROM players WHERE player_id = ?', (player_id,))
        player = cur.fetchone()

        if player is None:
            session.clear()
            session['session_uuid'] = str(uuid.uuid4())
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

    objects = []
    story_log = [""]
    location = ""

    if player_id: 
        cur = db.execute("SELECT entry, category FROM story_log WHERE player_id = ? ORDER BY timestamp ASC", (player_id,))
        story_log = cur.fetchall()

        cur = db.execute('SELECT * FROM players WHERE player_id = ?', (player_id,))
        player = cur.fetchone()
        location_id = player['current_location_id']
        print("Looking for location id: " + str(location_id))
        cur = db.execute('SELECT * FROM locations WHERE location_id = ?', (location_id,))
        location = cur.fetchone()
        print(f"Location query result: {dict(location) if location else 'None'}")

        # checking all locations in the location database to debug location id 0 not found
        cur = db.execute('SELECT location_id, location_name FROM locations ORDER BY location_id')
        all_locations = cur.fetchall()
        print(f"All locations in database: {[(loc['location_id'], loc['location_name']) for loc in all_locations]}")

        cur = db.execute("SELECT * FROM objects WHERE location_id = ?", (location_id, )).fetchall()
        objects = cur
    
    error = False
    if not player_id: 
        error = True
    return render_template('index.html', story_log=story_log, location=location, objects=objects, error=error)

@bp.route('/', methods=['POST'])
def user_input(): 
    text = request.form['user_input']
    db = get_db()
    player_id = session.get('player_id')
    process(text, db, player_id)
    return redirect('/')