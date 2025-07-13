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

    # quest definitions (includes a name and description)
    quests = [
        (0, "Leave the room", "Exit through the door"), 
    ]
    # send quests to database
    for quest_id, name, desc in quests: 
        db.execute("INSERT OR IGNORE INTO quest_definitions (quest_id, quest_name, description) VALUES (?, ?, ?)", (quest_id, name, desc))
    
    locations = [
        (0, "Control Room", "A dusty old room with storage crates all around and several mysterious-looking switches and buttons")
    ]
    for location_id, name, desc in locations:
        db.execute("INSERT OR IGNORE INTO locations (location_id, location_name, description) VALUES (?, ?, ?)", (location_id, name, desc))

    story = [
        (0, "You find yourself in an abandoned control room")
    ]
    for story_id, entry in story: 
        db.execute("INSERT OR IGNORE INTO full_story (story_element_id, entry) VALUES (?, ?)", (story_id, entry))
    
    db.commit()