from flask import session

def initialize_new_player(db, player_id, num_initial): 
    db.execute('INSERT INTO quest_log (player_id, quest_id, discovered, started) VALUES (?, ?, ?, ?)', (player_id, 0, True, True))
    for i in range(num_initial): 
        db.execute('INSERT INTO story_log (player_id, story_id) VALUES (?, ?)', (player_id, i))

    # just to make sure that the player's location is set
    db.execute('UPDATE players SET current_location_id = ? WHERE player_id = ?', (0, player_id))
    db.commit()

def process(text, db, player_id): 
    text = text.strip().lower()
    s = ""
    parts = text.split()
    s = parse(parts, db, player_id)
    db.execute('INSERT INTO story_log (player_id, custom_entry) VALUES (?, ?)', (player_id, s))
    db.commit()
    return s

commands = ['inspect', 'grab', 'open']

def parse(parts, db, player_id): 
    response = ""
    room_id = get_curr_room_id(db=db)
    cur = db.execute('SELECT * FROM objects WHERE location_id = ?', (room_id, ))
    object_entries = cur.fetchall()
    objects = []
    objects_plus_synonyms = []
    # need to update for multi-word objects
    for i, object in enumerate(object_entries): 
        objects.append(object['name'].lower())
        cur = db.execute('SELECT * FROM object_synonyms WHERE object_id = ?', (object['object_id']))
        synonyms = cur.fetchall()
        for i, synonym in synonyms: 
            objects_plus_synonyms.append(synonym)
    if parts[0] == "clear": 
        db.execute('DELETE FROM story_log WHERE player_id = ?', (player_id,))
        response = "Story log cleared"
        return response
    elif parts[0] == "help": 
        response = "The available commands are "
        for i, command in enumerate(commands): 
            if i == len(commands) - 1: 
                response += command + ". "
            else: 
                response += command + ", "
    elif len(parts) < 2: 
        response = "Please enter at least a command and an object"
        return response
    elif parts[0] not in commands: 
        response = "Please enter a valid command (inspect, grab, open)"
        return response
    elif parts[1] not in objects_plus_synonyms and not (parts[1] + " "+ parts[2]) in objects_plus_synonyms: 
        response = "Please enter a valid object: "
        for i, object in enumerate(objects): 
            if i == len(objects) - 1: 
                response += object
            else: 
                response += object + ", "
        return response
    elif parts[0] == "inspect": 
        if len(parts) > 2: 
            object_name = parts[1] + " " + parts[2]
        else: 
            object_name = parts[1]
        cur = db.execute('SELECT * FROM objects WHERE name = ?', (object_name, ))
        direct_object = cur.fetchone()
        response = direct_object['description'] 
    
    db.commit()
    
    return response

def get_curr_room_id(db): 
    player_id = session.get('player_id')
    cur = db.execute('SELECT * FROM players WHERE player_id = ?', (player_id,))
    player = cur.fetchone()
    location_id = player['current_location_id']
    return location_id