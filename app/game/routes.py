from flask import render_template, session, redirect, request, url_for
from app.game import bp
from app.db import get_db
from .utils import initialize_new_player, preprocess, parse, get_curr_room, process_command

@bp.before_app_request
def make_session_permanent(): 
    session.permanent = True

@bp.before_app_request
def check_player_id_exists():
    db = get_db()
    player_id = session.get('player_id')

    if not player_id:
        cur = db.execute('INSERT INTO players (nickname, current_location_id) VALUES (?, ?)', ('Guest', 1))
        db.commit()
        session['player_id'] = cur.lastrowid
        print(f"Created new player with id {cur.lastrowid}")
        initialize_new_player(db, session.get('player_id'), 4)
        return redirect(request.path)
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
        cur = db.execute('''
            SELECT qd.quest_name, qd.description, ql.discovered, ql.started, ql.completed
            FROM quest_log ql
            JOIN quest_definitions qd ON ql.quest_id = qd.quest_id
            WHERE ql.player_id = ?
        ''', (player_id,))
        quests = cur.fetchall()

        cur = db.execute('''
            SELECT 
                COALESCE(fs.entry, sl.custom_entry) as entry,
                COALESCE(fs.category, 'Response') as category
            FROM story_log sl
            LEFT JOIN full_story fs ON sl.story_id = fs.story_element_id
            WHERE sl.player_id = ?
            ORDER BY sl.timestamp ASC
        ''', (player_id,))
        story_log = cur.fetchall()

        location = get_curr_room(db=db)
    return render_template('index.html', quests=quests, story_log=story_log, location=location)

@bp.route('/', methods=['POST'])
def user_input(): 
    text = request.form['user_input']
    db = get_db()
    player_id = session.get('player_id')
    process_command(text, db, player_id)
    return redirect('/')