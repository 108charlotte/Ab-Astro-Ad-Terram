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

# TODO: #1 clean this up
def parse(parts, db, player_id): 
    response = ""
    if len(parts) < 1: 
        response = "Please enter at least one word"
    elif len(parts) < 2: 
        command = parts[0]
        match command: 
            case "clear": 
                db.execute('DELETE FROM story_log WHERE player_id = ?', (player_id,))
                response = "Story log cleared"
            case "help": 
                response = "The available commands are "
                for i, command in enumerate(commands): 
                    if i == len(commands) - 1: 
                        response += command + ". "
                    else: 
                        response += command + ", "
                response += ". Additionally, you can use the clear command to clear the console, and the help command to view all possible commands."
            case "inventory": 
                response = "Inventory: "
                cur = db.execute("SELECT item_name FROM inventory JOIN items ON inventory.item_id = items.item_id WHERE player_id = ?", (player_id, )).fetchall()
                if not cur: 
                    response = "Your inventory is empty."
                for i in range(len(cur)): 
                    response += cur[i]['item_name']
                    if i < len(cur) - 1: 
                        response += ", "
            case _: 
                response = "The only valid one-word commands are 'clear', 'help', and 'inventory.'"
        return response
    else: 
        command = parts[0].lower()
        if command in commands: 
            # get the objects currently in the room
            room_id = get_curr_room_id(db=db)
            object_rows = db.execute("SELECT * FROM objects WHERE location_id = ?", (room_id, ))
            object_rows = object_rows.fetchall()
            object_names_to_ids = {}
            for row in object_rows: 
                object_names_to_ids[row['name']] = row['object_id']
                synonym_rows = db.execute("SELECT * FROM object_synonyms WHERE object_id = ?", (row['object_id'], ))
                for s_row in synonym_rows: 
                    object_names_to_ids[s_row['synonym']] = s_row['object_id']

            if "with" in parts: 
                with_index = parts.index("with")
                target_object_items = parts[1:with_index - 1]
                target_object = build_string_of_list(target_object_items)
                target_item_items = parts[with_index + 1:]
                target_item = build_string_of_list(target_item_items)
            else: 
                target_object_items = parts[1:]
                target_object = build_string_of_list(target_object_items)

            # TODO: when entering a new room, all object descriptions should be printed
            # TODO: work on location linking logic for actual player movement
            # TODO: enable inventory additions for object interactions
            # check if the target object is valid
            if target_object in object_names_to_ids: 
                target_object_id = object_names_to_ids[target_object]
                cur = db.execute("SELECT * FROM object_interactions WHERE object_id = ? AND action = ?", (target_object_id, command))
                interaction_row = cur.fetchone()
                if interaction_row: 
                    inventory_item_ids = get_inventory_item_ids(player_id, db)
                    if interaction_row['requires_item_id'] and interaction_row['requires_item_id'] not in inventory_item_ids: 
                        response = "You are unable to " + command + " the " + target_object + " yet."
                    else: 
                        if interaction_row['requires_item_id']: 
                            response = interaction_row['item_requirement_usage_description']
                            response += "\n" + interaction_row['result']
                        elif interaction_row['location_link_id']: 
                            cur = db.execute("SELECT * FROM location_links WHERE link_id = ?", (interaction_row['location_link_id'], )).fetchone()
                            response = cur['travel_description']
                            db.execute("UPDATE players SET current_location_id = ? WHERE player_id = ?", (cur['to_location_id'], player_id))
                            cur = db.execute("SELECT * FROM locations WHERE location_id = ?", (cur['to_location_id'], )).fetchall()
                            response += cur['description']
                        else: 
                            response = interaction_row['result']
                        if interaction_row['gives_item_id'] is not None: 
                            # logic for adding item to inventory
                            if interaction_row['gives_item_id'] in inventory_item_ids: 
                                response = interaction_row['already_done_text']
                            else: 
                                db.execute("INSERT INTO inventory (player_id, item_id) VALUES (?, ?)", (player_id, interaction_row['gives_item_id']))
                                item_name = db.execute("SELECT item_name FROM items WHERE item_id = ?", (interaction_row['gives_item_id'], )).fetchone()
                                response += "\n+1: " + item_name['item_name'] + ". Type 'inventory' to see full inventory."
                else: 
                    if command == "inspect": 
                        cur = db.execute("SELECT * FROM objects WHERE object_id = ?", (target_object_id, )).fetchone()
                        response = cur['description']
                    else: 
                        response = "You cannot " + command + " the " + target_object
            else: 
                response = "Please enter a valid object name. The available are: "
                object_names_and_synonyms = list(object_names_to_ids.keys())
                object_and_synonym_ids = list(object_names_to_ids.values())
                most_recent_object_id = None
                object_name_list = []
                for i in range(len(object_and_synonym_ids)): 
                    if not most_recent_object_id or object_and_synonym_ids[i] != most_recent_object_id: 
                        object_name_list.append(object_names_and_synonyms[i])
                    most_recent_object_id = object_and_synonym_ids[i]
                response += build_string_of_list_w_commas(object_name_list)
        else: 
            response = "Please enter a valid command. Available commands are " + build_string_of_list_w_commas(commands)
    db.commit()
    return response

def get_inventory_item_ids(player_id, db): 
    cur = db.execute("SELECT item_id FROM inventory WHERE player_id = ?", (player_id, )).fetchall()
    inventory_item_ids = []
    for row in cur: 
        inventory_item_ids.append(row['item_id'])
    return inventory_item_ids

def build_string_of_list(list): 
    result = ""
    for i in range(len(list)): 
        result += list[i]
        if i != len(list) - 1: 
            result += " "
    return result

def build_string_of_list_w_commas(list): 
    result = ""
    for i in range(len(list)): 
        result += list[i]
        if i == len(list) - 2:
            result += ", and "
        elif i != len(list) - 1: 
            result += ", "
    return result

def get_curr_room_id(db): 
    player_id = session.get('player_id')
    cur = db.execute('SELECT * FROM players WHERE player_id = ?', (player_id,))
    player = cur.fetchone()
    location_id = player['current_location_id']
    return location_id