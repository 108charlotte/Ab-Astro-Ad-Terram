from flask import session

def initialize_new_player(db, player_id, num_initial): 
    db.execute('INSERT INTO quest_log (player_id, quest_id, discovered, started) VALUES (?, ?, ?, ?)', (player_id, 0, True, True))
    for i in range(num_initial): 
        db.execute('INSERT INTO story_log (player_id, story_id) VALUES (?, ?)', (player_id, i))

    # just to make sure that the player's location is set
    db.execute('UPDATE players SET current_location_id = ? WHERE player_id = ?', (0, player_id))
    db.commit()

def preprocess(text, db): 
    room = get_curr_room(db=db)
    text = text.strip().lower()
    s = ""
    if text == "": 
        s = "You must enter a command"
    else: 
        parts = text.split()
        s = parse(parts)
    return s

def parse(parts): 
    return "hi"


def get_curr_room(db): 
    player_id = session.get('player_id')
    cur = db.execute('SELECT * FROM players WHERE player_id = ?', (player_id,))
    player = cur.fetchone()
    location_id = player['current_location_id']
    cur = db.execute('SELECT * FROM locations WHERE location_id = ?', (location_id,))
    location = cur.fetchone()
    return location