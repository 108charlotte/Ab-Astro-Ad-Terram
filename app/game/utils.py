def initialize_new_player(db, player_id): 
    db.execute('INSERT INTO quest_log (player_id, quest_id, discovered, started) VALUES (?, ?, ?, ?)', (player_id, 0, True, True))
    db.execute('INSERT INTO story_log (player_id, story_id) VALUES (?, ?)', (player_id, 0))

    # just to make sure that the player's location is set
    db.execute('UPDATE players SET current_location_id = ? WHERE player_id = ?', (0, player_id))
    db.commit()