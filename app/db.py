import sqlite3
from datetime import datetime
import os

import click
from flask import current_app, g

def init_app(app): 
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)
    app.cli.add_command(populate_db_command)
    app.cli.add_command(reset_db_command)

def get_db(): 
    print('Current config keys:', current_app.config.keys())
    if 'db' not in g: 
        g.db = sqlite3.connect(
            current_app.config['DATABASE'], 
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row
    return g.db

def close_db(e=None):
    db = g.pop('db', None)
    if db is not None: 
        db.close()

def init_db(): 
    db = get_db()

    with current_app.open_resource('schema.sql') as f:
        db.executescript(f.read().decode('utf8'))

@click.command('reset-db')
def reset_db_command(): 
    close_db()
    db_path = current_app.config['DATABASE']

    if os.path.exists(db_path): 
        os.remove(db_path)
        click.echo(f"Deleted database file at {db_path}")
    else:
        click.echo(f"No database file found at {db_path}, skipping delete.")

    with current_app.app_context():
        init_db()
        populate_db()
    click.echo("Database reset: schema re-created and tables populated.")

@click.command('init-db')
def init_db_command(): 
    init_db()
    click.echo('Initialized the database.')

sqlite3.register_converter (
    "timestamp", lambda v: datetime.fromisoformat(v.decode())
)

@click.command('populate-db')
def populate_db_command(): 
    populate_db()
    click.echo('Populated the tables with initial data. ')

def populate_db(): 
    db = get_db()

    '''
    thinking...
    players should populate dynamically, along with story_log and quest_log. 
    quest_definitions needs to be populated.
    inventory should populate dynamically. 
    items needs to be populated. 
    locations needs to be populated, and so does location links. 
    story flags will populate dynamically, but the structure of this may change later. 
    dialogue_log will populate dynamically. 
    npcs needs to be populated. 
    dialogue_lines needs to be populated. 
    full_story needs to be populated. 
    REMEMBER TO USE INSERT OR IGNORE INTO when populating each table so that I can run this command again to update later. 
    '''

    locations = [
        (0, "Secondary Control Room", "a dusty old room with storage crates all around and several mysterious-looking switches and buttons"), 
        (1, "Upper Hallway", "a long, bare corridor with sharp turns and uniform walls of aluminum and large bolts holding the plates together"), 
        (2, "Captain's Quarters", ""), 
        (3, "Pilot's Quarters", ""),
        (4, "Chief Engineer's Quarters", ""), 
        (5, "Scientific Supervisor's Quarters", ""), 
        (6, "Chief Medical Consultant's Quarters", "")
    ]
    for location_id, name, desc in locations:
        db.execute("INSERT OR IGNORE INTO locations (location_id, location_name, description) VALUES (?, ?, ?)", (location_id, name, desc))

    quarters_door_message = "You carefully open the door and pass through. "

    location_links = [
        # ids autoincrement, values start at 1
        (1, 0, "You force open a very heavy and secure metal door. ", 0, None), 
        (2, 1, quarters_door_message, None, None), 
        (3, 1, quarters_door_message, None, None), 
        (4, 1, quarters_door_message, None, None), 
        (5, 1, quarters_door_message, None, None), 
        (6, 1, quarters_door_message, None, None), 
        (5, 6, "You are able to crawl through a tight squeeze-space and emerge from behind a cloth concealing the entrance on the other end, like you had to brush aside to enter.", None, None), 
        (0, 1, "You force open a very heavy and secure metal door. No key is required to get through on this side. ", None, None)
    ]
    for to_location_id, from_location_id, travel_description, requires_item_id, unlocks_flag_id in location_links: 
        db.execute("INSERT OR IGNORE INTO location_links (to_location_id, from_location_id, travel_description, requires_item_id, unlocks_flag_id) VALUES (?, ?, ?, ?, ?)", (to_location_id, from_location_id, travel_description, requires_item_id, unlocks_flag_id))
    
    hallway_door_description = "A standard-looking grey door, less heavy-duty than the one leading to the secondary control room. "
    objects = [
        # secondary control room
        (0, 0, "crates", "Numerous crates lie across the room gathering dust. You can't discern what's inside any of them from afar. "), 
        (1, 0, "door", "The only door out of the room appears to be locked. There is a small keyhold next to it. "), 
        (2, 0, "control panel", "The control panel takes up almost half of the room. It is riddled with levers, switches, and buttons, but all of the indicator lights are off. "), 
        #TODO: add story flag for switches + ability to activate with inspect
        (3, 0, "switches", "There is an assortment of odd-looking switches and buttons splayed across the massive control panel. "), 

        # hallway
        (4, 1, "first door on the left", hallway_door_description), 
        (5, 1, "second door on the left", hallway_door_description), 
        (6, 1, "first door on the right", hallway_door_description), 
        (7, 1, "second door on the right", hallway_door_description), 
        (8, 1, "secondary control room door", "A heavy-grade industrial metal door. ")
    ]
    for object_id, location_id, name, description in objects: 
        db.execute("INSERT OR IGNORE INTO objects (object_id, location_id, name, description) VALUES (?, ?, ?, ?)", (object_id, location_id, name, description))
    
    object_synonyms = [
        (0, "boxes"), 
        (1, "exit"), 
        (3, "levers"), 
        (3, "buttons")
    ]
    for object_id, synonym in object_synonyms: 
        db.execute("INSERT OR IGNORE INTO object_synonyms (object_id, synonym) VALUES (?, ?)", (object_id, synonym))

    story_flags = [
        (0, "Control room activated"), 
        (1, "Key grabbed"), 
    ]
    for story_flag_id, name in story_flags: 
        db.execute("INSERT OR IGNORE INTO story_flags (story_flag_id, flag_name) VALUES (?, ?)", (story_flag_id, name))
    
    items = [
        (0, "key", "A small brass key with a diamond tail."), 
    ]
    for item_id, name, description in items: 
        db.execute("INSERT OR IGNORE INTO items (item_id, item_name, description) VALUES (?, ?, ?)", (item_id, name, description))
    
    # maybe add a location link id for doors? 
    object_interactions = [
        (0, 0, "inspect", None, 
         "After more closely inspecting the crates, you notice that a smaller one on top of one of the stacks is slightly ajar. Inside of it lies a small brass key.", 
         None, 0, "Nothing else remains in the single crate you were able to open.", None), 
        (1, 0, "open", None, 
         "You are unable to open most of the crates. However, one small one on top of one of the stacks is slightly ajar, and when you open it you see a small brass key.", 
         None, 0, "Nothing else remains in the single crate you were able to open.", None), 
        (2, 1, "open", 1, None, 0, None, None, "You insert the brass key into the small keyhole on the side of the door."), 
        (3, 4, "open", 2, None, None, None, None, None), 
        (4, 5, "open", 3, None, None, None, None, None), 
        (5, 6, "open", 4, None, None, None, None, None), 
        (6, 7, "open", 5, None, None, None, None, None), 
        (7, 8, "open", 8, None, None, None, None, None), 
    ]
    for interaction_id, object_id, action, location_link_id, result, requires_item_id, gives_item_id, already_done_text, item_requirement_usage_description in object_interactions: 
        db.execute("INSERT OR IGNORE INTO object_interactions (interaction_id, object_id, action, location_link_id, result, requires_item_id, gives_item_id, already_done_text, item_requirement_usage_description) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", (interaction_id, object_id, action, location_link_id, result, requires_item_id, gives_item_id, already_done_text, item_requirement_usage_description))
    
    db.commit()