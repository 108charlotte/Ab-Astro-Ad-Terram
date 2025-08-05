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

    locations = [
        (0, "Secondary Control Room", "a dusty old room with storage crates all around and several mysterious-looking switches and buttons"), 
        (1, "Upper Hallway", "a long, bare corridor with sharp turns and uniform walls of aluminum and large bolts holding the plates together"), 
        (2, "Captain's Quarters", "a medium dormitory-style quarters, containing a bed on the right side of the room with a bedside table, a desk facing the wall on the left of the room, and a small wardrobe on the left wall closest to the door. "), 
        (3, "Pilot's Quarters", "a medium dormitory-style quarters, with a bed and bedside table on the right, a desk on the left far wall, and a wardrobe on the left near wall. "),
        (4, "Chief Engineer's Quarters", "a medium dormitory-style quarters, with a bed and bedside table on the right, a desk on the far left wall, and a wardrobe on the near left wall. Compared to the other dormitories, it appears to be the least organized, with several items seemingly haphazardly spread around. "), 
        (5, "Scientific Supervisor's Quarters", "a medium dormitory-style quarters, with a bed and bedside table on the right, a desk on the far left wall, and a wardrobe on the near left wall. There are very few items furnishing the room, and from what you can see, nothing is out of place. "), 
        (6, "Chief Medical Consultant's Quarters", "a medium dormitory-style quarters, with a bed and bedside table on the right, a desk on the far left wall, and a wardobe on the near left wall. Everything is very orderly and nothing appears to be out of place. "), 
        (7, "Main Control Room", "an expansive control room with large windows and at least twenty chairs at the massive control panel which surrounds the room. ") # if control panel activated, can see thru windows
    ]
    for location_id, name, desc in locations:
        db.execute("INSERT OR IGNORE INTO locations (location_id, location_name, description) VALUES (?, ?, ?)", (location_id, name, desc))

    quarters_door_message = "You carefully open the door and enter the room. "

    location_links = [
        # ids autoincrement, values start at 1
        # out of control room, into hallway
        (1, 0, "You force open a very heavy and secure metal door. "),
        # from hallway into dorms 
        (2, 1, quarters_door_message), 
        (3, 1, quarters_door_message), 
        (4, 1, quarters_door_message), 
        (5, 1, quarters_door_message), 
        (6, 1, quarters_door_message), 
        # secret passageway (to-be implemented)
        (5, 6, "You are able to crawl through a tight squeeze-space and emerge from behind a cloth concealing the entrance on the other end, like you had to brush aside to enter."), 
        # into control room from hallway
        (0, 1, "You force open a very heavy and secure metal door. No key is required to get through on this side. "), 
        # into hallway from dorms
        (1, 2, quarters_door_message), 
        (1, 3, quarters_door_message), 
        (1, 4, quarters_door_message), 
        (1, 5, quarters_door_message), 
        (1, 6, quarters_door_message), 
        # to primary control room from hallway
        (7, 1, "After scanning the keycard, the heavy industrial door gracefully slides open. "), 
        # to hallway from primary control room
        (1, 7, "The heavy industrial door gracefully slides open automatically, no keycard required. ")
    ]
    for to_location_id, from_location_id, travel_description in location_links: 
        db.execute("INSERT OR IGNORE INTO location_links (to_location_id, from_location_id, travel_description) VALUES (?, ?, ?)", (to_location_id, from_location_id, travel_description))
    
    hallway_door_description = "A standard-looking grey door, less heavy-duty than the one leading to the secondary control room. "
    objects = [
        # secondary control room
        (0, 0, "crates", "Numerous crates lie across the room gathering dust. You can't discern what's inside any of them from afar. "), 
        (1, 0, "door", "The only door out of the room appears to be locked. There is a small keyhold next to it. "), 
        (2, 0, "control panel", "The control panel takes up almost half of the room. It is riddled with levers, switches, and buttons, but all of the indicator lights are off. "), 
        (3, 0, "switches", "There is an assortment of odd-looking switches and buttons splayed across the massive control panel. "), 

        # hallway
        (4, 1, "first door on the left", hallway_door_description + "The door is labelled 'captain.'"), 
        (5, 1, "second door on the left", hallway_door_description + "The door is labelled 'pilot.'"), 
        (6, 1, "first door on the right", hallway_door_description + "The door is labelled 'chief engineer'"), 
        (7, 1, "second door on the right", hallway_door_description + "The door is labelled 'scientific supervisor.'"), 
        (8, 1, "third door on the right", hallway_door_description + "The door is labelled 'chief medical consultant.'"), 
        (9, 1, "secondary control room door", "A heavy-grade industrial metal door. "), 

        # captain's quarters
        (10, 2, "desk", "A simple metal desk frame, with locked drawers (appears to use fingerprint recognition) and miscellaneous papers scattered across it with no apparent connections to each other. There are a few postcards, several letters from family and other miscellaneous papers, but nothing you can make any sense of."), 
        (11, 2, "bed", "An economical metal frame with a sad-looking mattress. You wonder how anyone is able to sleep on it. "), 
        (12, 2, "wardrobe", "When you open the doors of the wardrobe, you see a single rack and drawer. From what you can tell, there are two sets of the same blue and grey uniform. On the shirt, there is a small star logo with embroidered text beneath it reading 'astro' (see the favicon for this page for the design!), and beneath that there is more text reading 'CAPTAIN.'"), 
        (13, 2, "bedside table", "A simple and unremarkable metal bedside table. Barely more than a frame, all it can fit is a single small lamp. Turning it on and off does not appear to have any effect. "), 
        (14, 2, "door to hallway", hallway_door_description), 

        # pilot's quarters
        (15, 3, "desk", "A simple metal desk frame, with locked drawers (appears to use fingerprint recognition). The desk is entirely empty save for a lamp, which you cannot get to turn on despite pressing the switch several times. "), 
        (16, 3, "bed", "A simple, economical metal bed frame with a bare mattress. It looks awfully uncomfortable. "),
        (17, 3, "wardrobe", "Opening the doors of the wardrobe reveals two blue and grey uniforms, each with a logo and embroidered text beneath them reading 'astro' (see page favicon for what this looks like!). Beneath the logo and text, there is more text reading 'PILOT.' "), 
        (18, 3, "bedside table", "A short metal table with no drawers and nothing on it. As unremarkable as the bed. "), 
        (19, 3, "door to hallway", hallway_door_description), 

        # chief engineer's quarters
        (20, 4, "desk", "A simple metal desk frame, with locked drawers (appears to use fingerprint recognition). The top is scattered with blueprints of the ship and miscellaneous technical diagrams which you have trouble making sense of. "), 
        (21, 4, "bed", "A simple, economical metal bed frame with a bare mattress. Looks uncomfortable. "), 
        (22, 4, "wardrobe", ""), 
        (23, 4, "bedside table", "A short and rather unremarkable metal table with no drawers. "), 
        (24, 4, "door to hallway", hallway_door_description), 

        # scientific supervisor's quarters
        (25, 5, "desk", "A simple metal desk frame, with locked drawers (appears to use fingerprint recognition), completely empty save for a rather sad looking lamp in the corner. You cannot figure out how to turn it on, and there is nothing else you can investigate on the desk. "), 
        (26, 5, "bed", "A simple, economical metal bed frame with a bare mattress. No-frills, and takes up no more space than it needs to. "), 
        (27, 5, "wardrobe", ""), 
        (28, 5, "bedside table", ""), 
        (29, 5, "door to hallway", hallway_door_description), 

        # chief medical consultant's quarters
        (30, 6, "desk", ""), 
        (31, 6, "bed", ""), 
        (32, 6, "wardrobe", ""), 
        (33, 6, "bedside table", ""), 
        (34, 6, "door to hallway", hallway_door_description),

        # hallway to primary control room
        (35, 1, "door at end of hallway (past dorms)", "A heavy industrial-grade door, similar to the one leading to the secondary control room. You don't think you could force it open if you tried. "), 
        # primary control room to hallway
        (36, 7, "door to main hallway", "A heavy industrial-grade door. It opens automatically, and you don't think you could force it to open otherwise if you tried. "), 
        # primary control room
        (37, 7, "windows", ""), 
        (38, 7, "control panel", ""), 
    ]
    for object_id, location_id, name, description in objects: 
        db.execute("INSERT OR IGNORE INTO objects (object_id, location_id, name, description) VALUES (?, ?, ?, ?)", (object_id, location_id, name, description))
    
    object_synonyms = [
        (0, "boxes"), 
        (1, "exit"), 
        (3, "levers"), 
        (3, "buttons"), 
        (35, "door at end of hallway"), 
        (35, "door at the end of the hallway"), 
        (35, "door at the end of the hallway (past doorms)"), 
        (35, "door past dorms"), 
        (4, "1st door on left"), 
        (4, "1st door on the left"),
        (4, "first door on left"), 
        (5, "2nd door on the left"), 
        (5, "2nd door on left"), 
        (5, "second door on left"), 
        (6, "1st door on right"), 
        (6, "1st door on the right"), 
        (6, "first door on right"), 
        (7, "2nd door on right"), 
        (7, "2nd door on the right"), 
        (7, "second door on right"), 
        (8, "3rd door on right"), 
        (8, "3rd door on the right"),
        (8, "third door on right"), 
        (37, "window"), 
        (13, "table"), 
        (18, "table"), 
        (23, "table"), 
        (28, "table"), 
        (33, "table"), 
        (14, "door"), 
        (19, "door"), 
        (24, "door"), 
        (29, "door"), 
        (34, "door")
    ]
    for object_id, synonym in object_synonyms: 
        db.execute("INSERT OR IGNORE INTO object_synonyms (object_id, synonym) VALUES (?, ?)", (object_id, synonym))

    story_flags = [
        (0, "Secondary control room switches"),  
    ]
    for story_flag_id, name in story_flags: 
        db.execute("INSERT OR IGNORE INTO story_flags (story_flag_id, flag_name) VALUES (?, ?)", (story_flag_id, name))
    
    items = [
        (0, "key", "A small brass key with a diamond tail."), 
        (1, "reports", "Several important-looking reports from the captain's desk, one from each division. "), 
        (2, "blueprints", "A collection of blueprints of the ship from the chief engineer's quarters. "), 
        (3, "keycard", "An unlabelled keycard from the chief engineer's dormitory. ")
    ]
    for item_id, name, description in items: 
        db.execute("INSERT OR IGNORE INTO items (item_id, item_name, description) VALUES (?, ?, ?)", (item_id, name, description))
    
    # maybe add a location link id for doors? 
    object_interactions = [
        (0, 0, "inspect", None, 
         "After more closely inspecting the crates, you notice that a smaller one on top of one of the stacks is slightly ajar. Inside of it lies a small brass key.", 
         None, 0, "Nothing else remains in the single crate you were able to open.", None, None, None, None), 
        (1, 0, "open", None, 
         "You are unable to open most of the crates. However, one small one on top of one of the stacks is slightly ajar, and when you open it you see a small brass key.", 
         None, 0, "Nothing else remains in the single crate you were able to open.", None, None, None, None), 
        (2, 1, "open", 1, None, 0, None, None, "You insert the brass key into the small keyhole on the side of the door.", None, None, None), 
        # hallway to dormitories and back to secondary control room
        (3, 4, "open", 2, None, None, None, None, None, None, None, None), 
        (4, 5, "open", 3, None, None, None, None, None, None, None, None), 
        (5, 6, "open", 4, None, None, None, None, None, None, None, None), 
        (6, 7, "open", 5, None, None, None, None, None, None, None, None), 
        (7, 8, "open", 6, None, None, None, None, None, None, None, None), 
        (8, 9, "open", 8, None, None, None, None, None, None, None, None), 
        # captain's door to hallway
        (9, 14, "open", 9, None, None, None, None, None, None, None, None), 
        # special interaction logics
        (10, 10, "inspect", None, 
         "A simple metal desk frame, with locked drawers (appears to use fingerprint recognition) and miscellaneous papers scattered across it with no apparent connections to each other. There are a few postcards, several letters from family, reports from each department (science, engineering, medical), but nothing you can make any sense of. Nevertheless, you decide to pocket any and everything that looks important, just in case you might need it later. ", 
         None, 1, "You have taken everything from the desk that looks useful to you. ", None, None, None, None), 
        (11, 3, "inspect", None, 
         "There is an assortment of odd-looking switches and buttons splayed across the massive control panel. After fiddling with a few, you are able to make an indicator light come on, and after a few seconds of flashing the rest of the control panel lights up. ", 
         None, None, "The indicator lights do not appear to turn off or change, no matter how many switches you press. ", None, 0, None, None), 
        (12, 20, "inspect", None, 
         "A simple metal desk frame, with locked drawers (appears to use fingerprint recognition). The top is scattered with blueprints of the ship and miscellaneous technical diagrams which you have trouble making sense of, but you decide to pocket a few anyways. Maybe they'll be useful later? ", 
         None, 2, "Nothing else on the desk is of note. ", None, None, None, None), 
        (13, 23, "inspect", None, 
         "A short and rather unremarkable metal table with no drawers. On  top of it you see a keycard. ", 
         None, 3, "There is nothing else on the bedside table. ", None, None, None, None), 
        # pilot, engineer, scientist, and medical doors to hallway
        (14, 19, "open", 10, None, None, None, None, None, None, None, None), 
        (15, 24, "open", 11, None, None, None, None, None, None, None, None), 
        (16, 29, "open", 12, None, None, None, None, None, None, None, None), 
        (17, 34, "open", 13, None, None, None, None, None, None, None, None), 
        # primary control room (doors in and out)
        (18, 35, "open", 14, None, 3, None, None, "You tap the keycard from the chief engineer's dorm on a small ID scanner next to the door. The light on the scanner changes from red to green. ", None, None, None), 
        (19, 36, "open", 15, None, None, None, None, None, None, None, None), 
        # primary control room (windows and control panel logic based on story flag)
        (20, 37, "inspect", None, 
         "Above the control panel is a beautiful view of a brownish-red planet, not like anything you've ever known. There is nothing but haze in the distance, and it is relatively flat with several hills. ", 
         None, None, None, None, 
         None, 0, "The windows are blacked out and you are unable to see through them. "), 
        (21, 38, "inspect", None, 
         "The control panel appears to be activated, just like the one in the secondary control room. There are a variety of indicator lights, but you don't understand how to operate the ship. ", 
         None, None, None, None, 
         None, 0, "The control panel is just like the one in the secondary control room but much, much larger, spanning every wall except for the one occupied by the door to the hallway. There are numerous buttons and switches, but pressing them has no visible effect. ")
    ]
    for interaction_id, object_id, action, location_link_id, result, requires_item_id, gives_item_id, already_done_text, item_requirement_usage_description, activates_story_flag_id, requires_story_flag_id, requirements_not_fulfilled_text in object_interactions: 
        db.execute("INSERT OR IGNORE INTO object_interactions (interaction_id, object_id, action, location_link_id, result, requires_item_id, gives_item_id, already_done_text, item_requirement_usage_description, activates_story_flag_id, requires_story_flag_id, requirements_not_fulfilled_text) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", (interaction_id, object_id, action, location_link_id, result, requires_item_id, gives_item_id, already_done_text, item_requirement_usage_description, activates_story_flag_id, requires_story_flag_id, requirements_not_fulfilled_text))
    
    db.commit()