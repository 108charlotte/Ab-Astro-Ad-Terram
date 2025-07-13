/* tables:
 * players (player_id, nickname, current_location_id)
 * story_log (player_id, entry, timestamp)
 * quest_log (player_id, quest_id, discovered (true/false), started (true/false), completed (true/false))
 * quest_definitions (quest_id, quest_name, description)
 * inventory (player_id, item_id, quantity)
 * items (item_id, item_name, description)
 * locations (location_id, location_name, description)
 * player_locations (player_id, location_id, unlocked (true/false), visited (true/false))
 * location_links (from_location_id, to_location_id, travel_description, requires_item_id (default NULL), bidirectional (true/false))
 * story_flags (player_id, flag_name, value)
 * dialogue_log (player_id, npc_id, dialogue_id, timestamp)
 * npcs (npc_id, name, description)
 * dialogue_lines (dialogue_id, npc_id, text, next_dialogue_id, trigger_flag, unlocks_flag)
*/

CREATE TABLE IF NOT EXISTS players (
    player_id INTEGER PRIMARY KEY AUTOINCREMENT,
    nickname TEXT NOT NULL, 
    current_location_id INTEGER, 
    FOREIGN KEY (current_location_id) REFERENCES locations(location_id)
); 

CREATE TABLE IF NOT EXISTS story_log (
    player_id INTEGER, 
    entry TEXT NOT NULL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP, 
    FOREIGN KEY (player_id) REFERENCES players(player_id)
); 

CREATE TABLE IF NOT EXISTS quest_log (
    player_id INTEGER, 
    quest_id INTEGER PRIMARY KEY AUTOINCREMENT, 
    discovered BOOLEAN DEFAULT FALSE, 
    started BOOLEAN DEFAULT FALSE,
    completed BOOLEAN DEFAULT FALSE, 
    FOREIGN KEY (player_id) REFERENCES players(player_id)
); 

CREATE TABLE IF NOT EXISTS quest_definitions (
    quest_id INTEGER, 
    quest_name TEXT NOT NULL,
    description TEXT, 
    FOREIGN KEY (quest_id) REFERENCES quest_log(quest_id)
); 

CREATE TABLE IF NOT EXISTS inventory (
    player_id INTEGER, 
    item_id INTEGER, 
    quantity INTEGER DEFAULT 1, 
    FOREIGN KEY (player_id) REFERENCES players(player_id),
    FOREIGN KEY (item_id) REFERENCES items(item_id)
); 

CREATE TABLE IF NOT EXISTS items (
    item_id INTEGER PRIMARY KEY AUTOINCREMENT,
    item_name TEXT NOT NULL,
    description TEXT
); 

CREATE TABLE IF NOT EXISTS locations (
    location_id INTEGER PRIMARY KEY AUTOINCREMENT, 
    location_name TEXT NOT NULL, 
    description TEXT
); 

CREATE TABLE IF NOT EXISTS player_locations (
    player_id INTEGER, 
    unlocked BOOLEAN DEFAULT FALSE, 
    visited BOOLEAN DEFAULT FALSE, 
    FOREIGN KEY (player_id) REFERENCES players(player_id)
); 

CREATE TABLE IF NOT EXISTS location_links (
    to_location_id INTEGER, 
    from_location_id INTEGER, 
    travel_description TEXT, 
    FOREIGN KEY (to_location_id) REFERENCES locations(location_id), 
    FOREIGN KEY (from_location_id) REFERENCES locations(location_id)
); 

CREATE TABLE IF NOT EXISTS story_flags (
    player_id INTEGER, 
    story_flag_id INTEGER PRIMARY KEY AUTOINCREMENT, 
    flag_name TEXT NOT NULL, 
    value BOOLEAN DEFAULT FALSE, 
    FOREIGN KEY (player_id) REFERENCES players(player_id)
); 

CREATE TABLE IF NOT EXISTS dialogue_log (
    player_id INTEGER, 
    dialogue_id INTEGER, 
    current BOOLEAN DEFAULT FALSE, 
    FOREIGN KEY (player_id) REFERENCES players(player_id), 
    FOREIGN KEY (dialogue_id) REFERENCES dialogue_lines(dialogue_id)
); 

CREATE TABLE IF NOT EXISTS npcs (
    npc_id INTEGER PRIMARY KEY AUTOINCREMENT, 
    description TEXT
); 

CREATE TABLE IF NOT EXISTS dialogue_lines (
    dialogue_id INTEGER PRIMARY KEY AUTOINCREMENT, 
    npc_id INTEGER, 
    text TEXT, 
    next_dialogue_id INTEGER, 
    trigger_flag_id INTEGER, 
    unlocks_flag_id INTEGER, 
    FOREIGN KEY (npc_id) REFERENCES npcs(npc_id), 
    FOREIGN KEY (next_dialogue_id) REFERENCES dialogue_lines(dialogue_id), 
    FOREIGN KEY (trigger_flag_id) REFERENCES story_flags(story_flag_id), 
    FOREIGN KEY (unlocks_flag_id) REFERENCES story_flags(story_flag_id)
); 