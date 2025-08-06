CREATE TABLE IF NOT EXISTS players (
    player_id INTEGER PRIMARY KEY,
    current_location_id INTEGER, 
    FOREIGN KEY (current_location_id) REFERENCES locations(location_id)
); 

CREATE TABLE IF NOT EXISTS story_flags (
    story_flag_id INTEGER PRIMARY KEY AUTOINCREMENT, 
    flag_name TEXT NOT NULL
); 

CREATE TABLE IF NOT EXISTS story_log (
    player_id INTEGER, 
    entry TEXT, 
    category TEXT, 
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (player_id) REFERENCES players(player_id)
); 

CREATE TABLE IF NOT EXISTS inventory (
    player_id INTEGER, 
    item_id INTEGER, 
    PRIMARY KEY (player_id, item_id),  
    FOREIGN KEY (player_id) REFERENCES players(player_id),
    FOREIGN KEY (item_id) REFERENCES items(item_id)
); 

CREATE TABLE IF NOT EXISTS items (
    item_id INTEGER PRIMARY KEY AUTOINCREMENT,
    item_name TEXT NOT NULL,
    description TEXT
); 

CREATE TABLE IF NOT EXISTS locations (
    location_id INTEGER PRIMARY KEY, 
    location_name TEXT NOT NULL, 
    description TEXT
); 

CREATE TABLE IF NOT EXISTS player_locations (
    player_id INTEGER, 
    location_id INTEGER, 
    unlocked BOOLEAN DEFAULT FALSE, 
    visited BOOLEAN DEFAULT FALSE, 
    PRIMARY KEY (player_id, location_id),
    FOREIGN KEY (player_id) REFERENCES players(player_id), 
    FOREIGN KEY (location_id) REFERENCES locations(location_id)
); 

CREATE TABLE IF NOT EXISTS location_links (
    link_id INTEGER PRIMARY KEY AUTOINCREMENT, 
    to_location_id INTEGER, 
    from_location_id INTEGER, 
    travel_description TEXT, 
    FOREIGN KEY (to_location_id) REFERENCES locations(location_id), 
    FOREIGN KEY (from_location_id) REFERENCES locations(location_id)
); 

CREATE TABLE IF NOT EXISTS triggered_story_flags (
    player_id INTEGER, 
    story_flag_id INTEGER, 
    FOREIGN KEY (player_id) REFERENCES players(player_id),
    FOREIGN KEY (story_flag_id) REFERENCES story_flags(story_flag_id)
); 

/* table for items in each room, by location id */

/* 
may change architecture so that certain commands called on certain objects will activate story flags, but idk how to do that rn and I will have to brainstorm more on the architecture
*/

CREATE TABLE IF NOT EXISTS objects (
    object_id INTEGER PRIMARY KEY, 
    location_id INTEGER,  
    name TEXT NOT NULL, 
    description TEXT, 
    FOREIGN KEY (location_id) REFERENCES locations(location_id)
);

CREATE TABLE IF NOT EXISTS object_interactions (
    interaction_id INTEGER PRIMARY KEY, 
    object_id INTEGER, 
    action TEXT NOT NULL, 
    result TEXT, 
    requires_item_id INTEGER, 
    gives_item_id INTEGER, 
    already_done_text TEXT, 
    location_link_id INTEGER, 
    item_requirement_usage_description TEXT, 
    activates_story_flag_id INTEGER, 
    requires_story_flag_id INTEGER, 
    requirements_not_fulfilled_text TEXT, 
    FOREIGN KEY (object_id) REFERENCES objects(object_id), 
    FOREIGN KEY (requires_item_id) REFERENCES items(item_id), 
    FOREIGN KEY (gives_item_id) REFERENCES items(item_id), 
    FOREIGN KEY (activates_story_flag_id) REFERENCES story_flags(story_flag_id), 
    FOREIGN KEY (requires_story_flag_id) REFERENCES story_flags(story_flag_id)
); 

CREATE TABLE IF NOT EXISTS object_synonyms (
    object_id INTEGER, 
    synonym TEXT, 
    PRIMARY KEY (object_id, synonym), 
    FOREIGN KEY (object_id) REFERENCES objects(object_id)
); 