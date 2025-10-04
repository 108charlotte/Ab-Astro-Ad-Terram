from flask import session

def initialize_new_player(db, player_id): 
    story = [
        ("You find yourself in an abandoned control room", "Description"), 
        ("What would you like to do?", "Continue"), 
        ("Available objects are: crates, door, control panel, and switches", "Hint"), 
        ("See the side panel for room description. This will update as you change rooms.", "Instruction"), 
        ("Hint: Try 'inspect boxes'", "Hint"), 
        ("Enter 'help' for more assistance.", "Instruction"), 
    ]

    for entry, category in story: 
        db.execute("INSERT OR IGNORE INTO story_log (player_id, entry, category) VALUES (?, ?, ?)", (player_id, entry, category))
    
    # just to make sure that the player's location is set
    db.execute('UPDATE players SET current_location_id = ? WHERE player_id = ?', (0, player_id))
    db.commit()

def process(text, db, player_id): 
    text = text.strip().lower()
    s = ""
    parts = text.split()
    s = parse(parts, db, player_id)
    for entry, category in s: 
        db.execute('INSERT INTO story_log (player_id, entry, category) VALUES (?, ?, ?)', (player_id, entry, category))
    db.commit()

commands = ['inspect', 'open']

def parse(parts, db, player_id): 
    response = [("", "")]
    entry = ""
    if len(parts) < 1: 
        response = [("Please enter at least one word", "Warning")]
    elif len(parts) < 2: 
        command = parts[0]
        match command: 
            case "clear": 
                db.execute('DELETE FROM story_log WHERE player_id = ?', (player_id,))
                response = [("Story log cleared", "Info")]
            case "help": 
                entry = "The available commands are "
                for i, command in enumerate(commands): 
                    if i == len(commands) - 1: 
                        entry += command + ". "
                    else: 
                        entry += command + ", "
                entry += "Additionally, you can use the clear command to clear the console, and the help command to view all possible commands. "
                response = [(entry, "Hint")]
                response.append(("Also, check the left side bar for a location, description, and available objects. ", "Hint"))
            case "inventory": 
                entry = "Inventory: "
                cur = db.execute("SELECT item_name FROM inventory JOIN items ON inventory.item_id = items.item_id WHERE player_id = ?", (player_id, )).fetchall()
                if not cur: 
                    entry = "Your inventory is empty."
                for i in range(len(cur)): 
                    entry += cur[i]['item_name']
                    if i < len(cur) - 1: 
                        entry += ", "
                response = [(entry, "Info")]
            case _: 
                response = [("The only valid one-word commands are 'clear', 'help', and 'inventory.'", "Warning")]
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
            # check if the target object is valid
            if target_object in object_names_to_ids: 
                target_object_id = object_names_to_ids[target_object]
                cur = db.execute("SELECT * FROM object_interactions WHERE object_id = ? AND action = ?", (target_object_id, command))
                interaction_row = cur.fetchone()
                if interaction_row: 
                    story_flags = get_triggered_story_flag_ids(player_id, db)
                    inventory_item_ids = get_inventory_item_ids(player_id, db)
                    if interaction_row['requires_item_id'] is not None and interaction_row['requires_item_id'] not in inventory_item_ids: 
                        if interaction_row['requirements_not_fulfilled_text']: 
                            response = [(interaction_row['requirements_not_fulfilled_text'], "")]
                        else: 
                            response = [("You are unable to " + command + " the " + target_object + " yet. ", "Warning")]
                    elif interaction_row['requires_story_flag_id'] is not None and interaction_row['requires_story_flag_id'] not in story_flags: 
                        if interaction_row['requirements_not_fulfilled_text']: 
                            response = [(interaction_row['requirements_not_fulfilled_text'], "")]
                        else: 
                            response = [("You are unable to " + command + " the " + target_object + " yet. ", "Warning")]
                    else: 
                        if interaction_row['requires_item_id']: 
                            entry_1 = interaction_row['item_requirement_usage_description']
                            response.append((entry_1, ""))
                            if interaction_row['result']: 
                                entry_2 = "\n" + interaction_row['result']
                                response.append((entry_2, ""))
                        if interaction_row['location_link_id']: 
                            cur = db.execute("SELECT * FROM location_links WHERE location_link_id = ?", (interaction_row['location_link_id'], )).fetchone()
                            entry_1 = cur['travel_description']
                            new_room_id = cur['to_location_id']
                            db.execute("UPDATE players SET current_location_id = ? WHERE player_id = ?", (new_room_id, player_id))
                            cur = db.execute("SELECT * FROM locations WHERE location_id = ?", (new_room_id, )).fetchone()
                            entry_2 = "You find yourself in " + cur['description']
                            entry_3 = "Available objects are: "
                            objects_in_new_room = db.execute("SELECT * FROM objects WHERE location_id = ?", (new_room_id, )).fetchall()
                            list_of_objects_in_new_room = []
                            for row in objects_in_new_room: 
                                list_of_objects_in_new_room.append(row['name'])
                            entry_3 += build_string_of_list_w_commas(list_of_objects_in_new_room)
                            response.append((entry_1, ""))
                            response.append((entry_2, ""))
                            response.append((entry_3, "Hint"))
                        if interaction_row['result']: 
                            response.append((interaction_row['result'], ""))
                        if interaction_row['gives_item_id'] is not None: # added is not None bc before 0 was registering as none
                            # logic for adding item to inventory
                            if interaction_row['gives_item_id'] in inventory_item_ids: 
                                response = [(interaction_row['already_done_text'], "")]
                            else: 
                                db.execute("INSERT INTO inventory (player_id, item_id) VALUES (?, ?)", (player_id, interaction_row['gives_item_id']))
                                item_name = db.execute("SELECT item_name FROM items WHERE item_id = ?", (interaction_row['gives_item_id'], )).fetchone()
                                response.append(("+1: " + item_name['item_name'], "Info"))
                                response.append(("Type 'inventory' to view full inventory. ", "Hint"))
                        if interaction_row['activates_story_flag_id'] is not None: 
                            cur = db.execute("SELECT * FROM triggered_story_flags WHERE story_flag_id = ? AND player_id = ?", (interaction_row['activates_story_flag_id'], player_id)).fetchone()
                            if cur is not None: 
                                response = [(interaction_row['already_done_text'], "")]
                            else: 
                                db.execute("INSERT INTO triggered_story_flags (player_id, story_flag_id) VALUES (?, ?)", (player_id, interaction_row['activates_story_flag_id']))
                                story_flag_name = db.execute("SELECT * FROM story_flags WHERE story_flag_id = ?", (interaction_row['activates_story_flag_id'], )).fetchone()['flag_name']
                                db.commit()
                                response.append(("STORY FLAG ACTIVATED: " + story_flag_name, "Info"))
                else: 
                    if command == "inspect": 
                        cur = db.execute("SELECT * FROM objects WHERE object_id = ?", (target_object_id, )).fetchone()
                        response = [(cur['description'], "")]
                    else: 
                        response = [("You cannot " + command + " the " + target_object, "Warning")]
            else: 
                entry = "Please enter a valid object name. The available are: "
                object_names_and_synonyms = list(object_names_to_ids.keys())
                object_and_synonym_ids = list(object_names_to_ids.values())
                most_recent_object_id = None
                object_name_list = []
                for i in range(len(object_and_synonym_ids)): 
                    if not most_recent_object_id or object_and_synonym_ids[i] != most_recent_object_id: 
                        object_name_list.append(object_names_and_synonyms[i])
                    most_recent_object_id = object_and_synonym_ids[i]
                entry += build_string_of_list_w_commas(object_name_list)
                response = [(entry, "Warning")]
        else: 
            response = [("Please enter a valid command. Available commands are " + build_string_of_list_w_commas(commands), "Warning")]
    db.commit()
    text = ""
    for row in response: 
        text, category = row
    if text != "": 
        return response
    else: 
        return [(entry, "")]

def get_triggered_story_flag_ids(player_id, db): 
    cur = db.execute("SELECT story_flag_id FROM triggered_story_flags WHERE player_id = ?", (player_id, )).fetchall()
    story_flag_ids = []
    for row in cur: 
        story_flag_ids.append(row['story_flag_id'])
    return story_flag_ids

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